from .models import Member, GivenPoint, GivenPointArchived, PointDistribution, Team
from .serializers import MemberSerializer, GivenPointArchivedSerializer, PointDistributionSerializer, \
    GivenPointSerializer, TeamSerializer
from .points_operation import validate_provisional_point_distribution, check_batch_includes_all_members, \
    check_all_point_values_are_valid
from .utils import is_current_week, get_member, filter_final_points_distributions, get_all_members, \
    get_given_point_models, get_monday_from_date, DATE_PATTERN, concatenate_and_hash
from .exceptions import NotCurrentWeekException

from django.http import Http404, JsonResponse
from django.db.utils import IntegrityError
from django.db.models import Sum, Count
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from pointdistribution.settings import VSTS_BASE_URL, SETTING_MANAGE_BASE_URL, SLACKBOT_URL

import requests
import logging


def construct_url_for_project(instance_name):
    request_url = VSTS_BASE_URL.format(instance_name)
    return request_url


@api_view(['PUT', 'POST'])
def create_superuser(request):
    user = User.objects.create_superuser(username="admin", password="admin", email="admin@admin.com")
    user.is_staff = True
    user.is_superuser = True
    user.save()

    return Response(status=status.HTTP_201_CREATED)


class TeamList(APIView):
    """
    Get all teams or a team with all its member
    Endpoint: **/v1/teams/all or **/v1/teams/team/?instance_id=2349
    """
    def get(self, request):
        instance_id = request.GET.get('instance_id', '')

        if instance_id is None or instance_id == '':
            # Return all teams
            teams = Team.objects.all()
            teams_list = dict()

            for team in teams:
                instance_id = team.instance_id
                instance_name = team.instance_name
                # Go fetch each team
                # TODO: Need to optimize this in the future
                members = Member.objects.all().filter(instance_id=instance_id)
                members_serializer = MemberSerializer(members, many=True)

                if instance_id == '':
                    continue
                else:
                    teams_list[instance_id] = {
                        'instance_name': instance_name,
                        'members': members_serializer.data
                    }

            return JsonResponse(teams_list)
        elif instance_id is not None and instance_id != '':

            try:
                team = Team.objects.get(instance_id=instance_id)

                members = Member.objects.all().filter(instance_id=instance_id)
                members_serializer = MemberSerializer(members, many=True)

                team_list = dict()
                team_list[instance_id] = {
                    'instance_name': team.instance_name,
                    'members': members_serializer.data
                }

                return JsonResponse(team_list)

            except Team.DoesNotExist as e:
                logging.warn(e)
                return Response(data=e, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class MemberList(APIView):
    """
    Get all the members, create a member

    Endpoint: **/v1/members/?instance_id=1234**  **/v1/members**

    Methods: *GET POST*
    """
    def get(self, request):
        instance_id = request.GET.get('instance_id', '')
        vsts_instance = request.GET.get('instance_name', '')
        user_email = request.GET.get('user_email', '')

        # Creating team
        try:
            logging.info("Creating team instance_id={} instance_name={}".format(instance_id, vsts_instance))
            Team.objects.create(instance_id=instance_id, instance_name=vsts_instance)

        except IntegrityError as e:
            logging.warn(e)

        logging.info("Received {} {} {}".format(instance_id, vsts_instance, user_email))

        params = {'instance_id': instance_id, 'user_email': user_email}
        vsts_token_request = requests.get(SETTING_MANAGE_BASE_URL + "v1/tokenstorage", params=params)
        vsts_token = vsts_token_request.json()['vsts_token']
        email_account_name = user_email.split('@')

        vsts_request_url = construct_url_for_project(vsts_instance)

        r = requests.get(vsts_request_url, auth=(email_account_name, vsts_token))

        projects = r.json()['value']

        for project in projects:
            # Get all team members
            project_id = project['id']
            r = requests.get('https://{}.visualstudio.com/DefaultCollection/_apis/projects/{}/teams'.format(vsts_instance,
                                                                                                      project_id),
                             auth=(email_account_name, vsts_token))
            team_id = r.json()['value'][0]['id']

            team_member_data = requests.get('https://{}.visualstudio.com/DefaultCollection/_apis/projects/{}/teams/{}/'
                                            'members?api_version=1.0'.format(vsts_instance, project_id, team_id),
                                            auth=(email_account_name, vsts_token))
            team_members = team_member_data.json()['value']

            for team_member in team_members:
                email = team_member['uniqueName']
                name = team_member['displayName']
                identifier = concatenate_and_hash(email, instance_id)

                logging.debug('email={} name={} identifier={}'.format(email, name, identifier))

                try:
                    logging.info("Create member entry")
                    Member.objects.create(email=email, name=name, instance_id=instance_id, identifier=identifier)

                except Member.DoesNotExist:
                    logging.info("Could not find member, creating new member with the following information;"
                                 "name={}, email{}, instance_id={}, identifier={}".format(name, email,
                                                                                          instance_id, identifier))
                    Member.objects.create(email=email, name=name, instance_id=instance_id, identifier=identifier)

                except IntegrityError as e:
                    logging.warn(e)

                except Exception as e:
                    logging.error("Something unexpected happened during the member filter", e)

        # Now fetch all the members and return them
        members = Member.objects.filter(instance_id=instance_id)
        logging.debug('Members=', members)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self, request):
        email = request.data['email']
        instance_id = request.data['instance_id']
        request.data['identifier'] = concatenate_and_hash(email, instance_id)
        serializer = MemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class MemberPointsHistory(APIView):
    """
    Get all the given points a user received

    Endpoint: **/v1/member/history/<email>/?instance_id=1234&filtered=true**

    Methods: *GET*
    """
    @staticmethod
    def get_given_points_member(member, instance_id):
        try:
            return GivenPointArchived.objects.filter(to_member=member, instance_id=instance_id)
        except GivenPointArchived.DoesNotExist:
            raise Http404

    def get(self, request, email):
        instance_id = request.GET.get('instance_id', '')
        is_filtered = request.GET.get('filtered', 'false')
        is_filtered = (True if is_filtered == 'true' else False)
        member = get_member(email, instance_id)
        given_points = self.get_given_points_member(member, instance_id)
        if is_filtered:
            filtered_results = {}
            for gp in given_points:
                key = concatenate_and_hash(gp.to_member, gp.week)
                filtered_results[key] = gp
            filtered_results_list = []
            for key, value in filtered_results.items():
                value.from_member = None
                filtered_results_list.append(value)
            filtered_results_list.sort(key=lambda r: r.week)
            serializer = GivenPointArchivedSerializer(filtered_results_list, many=True)
        else:
            given_points = self.get_given_points_member(member, instance_id)
            serializer = GivenPointArchivedSerializer(given_points, many=True)
        return Response(serializer.data)


class GivenPointsTeamTotal(APIView):
    """
    Get all the past point distributions

    Endpoint: **/v1/team/points/?instance_id=1234**

    Methods: *GET*
    """
    @staticmethod
    def get_aggregate(instance_id, members_list):
        members_to_total_points = {}
        for member in members_list:
            identifier = member.identifier
            name = member.name
            sum_points = GivenPointArchived.objects.filter(to_member=identifier, instance_id=instance_id)\
                .aggregate(sum=Sum('points'))
            members_to_total_points[name] = (sum_points['sum'] if sum_points['sum'] is not None else 0)
        return members_to_total_points

    def get(self, request):
        instance_id = request.GET.get('instance_id', '')
        members_list = get_all_members(instance_id)
        return Response(self.get_aggregate(instance_id, members_list))


class PointDistributionHistory(APIView):
    """
    Get all the past point distributions

    Endpoint: **/v1/points/distribution/history/?instance_id=1234**

    Methods: *GET*
    """
    def get(self, request):
        instance_id = request.GET.get('instance_id', '')
        point_distribution_history = filter_final_points_distributions(instance_id)
        serializer = PointDistributionSerializer(point_distribution_history, many=True)
        return Response(serializer.data)


class SendPoints(APIView):
    """
    Send points to team members. Date must be the current week

    Endpoint: **/v1/points/distribution/send**

    Methods: *POST PUT*

    Body:

    ```
    {
        "given_points": [
          {
            "to_member": "member1@email.com",
            "points": 30,
            "from_member": "me@me.com",
            "instance_id": "1234"
          },
          {
            "to_member": "member2@email.com",
            "points": 0,
            "from_member": "me@me.com",
            "instance_id": "1234"
          }
        ],
        "date": "2017-01-21",
        "instance_id": "1234"
    }
    ```
    """
    @staticmethod
    def get_or_create_point_distribution(date, week, instance_id, identifier):
        obj, _ = PointDistribution.objects.get_or_create(instance_id=instance_id, week=week, is_final=False,
                                                         identifier=identifier, defaults={'date': date})
        return obj

    def post(self, request):
        print(request.data)
        date = request.data['date']
        instance_id = request.data['instance_id']
        if not is_current_week(date, DATE_PATTERN):
            raise NotCurrentWeekException()
        week = get_monday_from_date(date, DATE_PATTERN)
        request.data['identifier'] = concatenate_and_hash(week, instance_id)
        point_distribution = self.get_or_create_point_distribution(date, week, instance_id, request.data['identifier'])
        members_set = set(get_all_members(instance_id).values_list('email', flat=True))
        given_points = request.data['given_points']
        check_batch_includes_all_members(given_points, members_set)
        check_all_point_values_are_valid(given_points)
        request.data['week'] = week

        for given_point in request.data['given_points']:
            given_point['week'] = week
            given_point['to_member'] = concatenate_and_hash(given_point['to_member'], instance_id)
            given_point['from_member'] = concatenate_and_hash(given_point['from_member'], instance_id)

        serializer = PointDistributionSerializer(point_distribution, data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        for given_point in serializer.data['given_points']:
            given_point['to_member'] = Member.objects.get(identifier=given_point['to_member']).email
            given_point['from_member'] = Member.objects.get(identifier=given_point['from_member']).email

        # Going through to send message to slackbot
        for given_point in serializer.data['given_points']:
            from_member = given_point['from_member']
            to_member = given_point['to_member']
            instance_id = given_point['instance_id']
            point = given_point['points']

            try:
                from_member_real_name = Member.objects.get(instance_id=instance_id, email=from_member).name

            except Member.DoesNotExist:
                from_member_real_name = from_member

            try:
                to_member_real_name = Member.objects.get(instance_id=instance_id, email=to_member).name

            except Member.DoesNotExist:
                to_member_real_name = to_member

            msg = '{} gave {} {} points'.format(from_member_real_name, to_member_real_name, point)
            logging.info("Created message={}".format(msg))
            data = {"instance_id": instance_id, "user_email": from_member, "msg": msg}
            print(data)
            slackbot_response = requests.post(SLACKBOT_URL + 'v1/api/send/', data=data)
            if slackbot_response.status_code == 202:
                logging.info("Successfully submitted to slack channel")
            else:
                logging.warn("Failed to submit messages to slack channel, status_code={}".format(slackbot_response.status_code))

        return Response(serializer.data)

    def put(self, request):
        date = request.data['date']
        instance_id = request.data['instance_id']
        if not is_current_week(date, DATE_PATTERN):
            raise NotCurrentWeekException()
        given_points = request.data['given_points']
        check_all_point_values_are_valid(given_points)
        week = get_monday_from_date(date, DATE_PATTERN)
        request.data['identifier'] = concatenate_and_hash(week, instance_id)
        given_points_models = get_given_point_models(given_points, week, instance_id)
        for idx, model in enumerate(given_points_models):
            given_points[idx]['from_member'] = concatenate_and_hash(given_points[idx]['from_member'], instance_id)
            given_points[idx]['to_member'] = concatenate_and_hash(given_points[idx]['to_member'], instance_id)
            given_points[idx]['week'] = week
            serializer = GivenPointSerializer(model, data=given_points[idx])
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        point_distribution = self.get_or_create_point_distribution(date, week, instance_id, request.data['identifier'])
        serializer = PointDistributionSerializer(point_distribution)
        for given_point in serializer.data['given_points']:
            given_point['to_member'] = Member.objects.get(identifier=given_point['to_member']).email
            given_point['from_member'] = Member.objects.get(identifier=given_point['from_member']).email

        # Going through to send message to slackbot
        for given_point in request.data['given_points']:
            from_member = given_point['from_member']
            to_member = given_point['to_member']
            instance_id = given_point['instance_id']
            point = given_point['points']

            try:
                from_member_real_name = Member.objects.filter(instance_id=instance_id, email=from_member)

            except Member.DoesNotExist:
                from_member_real_name = from_member

            try:
                to_member_real_name = Member.objects.filter(instance_id=instance_id, email=to_member)

            except Member.DoesNotExist:
                to_member_real_name = to_member

            msg = '{} gave {} {} points'.format(from_member_real_name, to_member_real_name, point)
            data = {'instance_id': instance_id, 'user_email': from_member, 'msg': msg}
            slackbot_response = requests.post(SLACKBOT_URL + 'v1/api/send/', data=data)
            if slackbot_response.status_code == 202:
                logging.info("Successfully submitted to slack channel")
            else:
                logging.warn("Failed to submit messages to slack channel")

        return Response(serializer.data)


class PointDistributionWeek(APIView):
    """
    Get a point distribution of a past week

    Endpoint: **/v1/point/distribution/YYYY-MM-DD/?instance_id=1234**

    Methods: *GET*
    """
    @staticmethod
    def get_object(week, instance_id):
        try:
            return PointDistribution.objects.get(instance_id=instance_id, week=week)
        except PointDistribution.DoesNotExist:
            raise Http404

    def get(self, request, week):
        instance_id = request.GET.get('instance_id', '')
        point_distribution = self.get_object(week, instance_id)
        serializer = PointDistributionSerializer(point_distribution)
        return Response(serializer.data)


class ValidateProvisionalPointDistribution(APIView):
    """
    Validate a point distribution

    Endpoint: **/v1/point/distribution/validate**

    Methods: *PUT*

    Body:

    `{"week":"YYYY-MM-DD", "instance_id":"1234"}`
    """
    @staticmethod
    def get_point_distribution(week, instance_id):
        try:
            return PointDistribution.objects.get(week=week, instance_id=instance_id)
        except PointDistribution.DoesNotExist:
            raise Http404

    def put(self, request):
        week = request.data['week']
        instance_id = request.data['instance_id']
        point_distribution = self.get_point_distribution(week, instance_id)
        members_set = set(get_all_members(instance_id))
        validate_provisional_point_distribution(point_distribution, members_set)
        point_distribution.is_final = True
        point_distribution.save()
        serializer = PointDistributionSerializer(point_distribution)
        return Response(serializer.data)


@api_view(['DELETE'])
def reset_database(request):
    Member.objects.all().delete()
    GivenPoint.objects.all().delete()
    PointDistribution.objects.all().delete()
    GivenPointArchived.objects.all().delete()

    return Response(data="Clear database from database", status=status.HTTP_200_OK)
