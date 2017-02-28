from .models import Member, GivenPoint, GivenPointArchived, PointDistribution
from .serializers import MemberSerializer, GivenPointArchivedSerializer, PointDistributionSerializer, \
    GivenPointSerializer
from .points_operation import validate_provisional_point_distribution, check_batch_includes_all_members, \
    check_all_point_values_are_valid
from .utils import is_current_week, get_member, filter_final_points_distributions, get_all_members, get_given_point_models
from .exceptions import NotCurrentWeekException

from django.http import Http404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response


class MemberList(generics.ListCreateAPIView):
    """
    Get all the members, create a member

    Endpoint: **/v1/members**

    Methods: *GET POST*
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class MemberPointsHistory(APIView):
    """
    Get all the given points a user received

    Endpoint: **/v1/member/history/<email>**

    Methods: *GET*
    """
    @staticmethod
    def get_given_points_member(member):
        try:
            return GivenPointArchived.objects.filter(to_member=member)
        except GivenPointArchived.DoesNotExist:
            raise Http404

    def get(self, request, email):
        member = get_member(email)
        given_points = self.get_given_points_member(member)
        serializer = GivenPointArchivedSerializer(given_points, many=True)
        return Response(serializer.data)


class PointDistributionHistory(APIView):
    """
    Get all the past point distributions

    Endpoint: **/v1/point/distribution/history**

    Methods: *GET*
    """
    def get(self, request):
        point_distribution_history = filter_final_points_distributions()
        serializer = PointDistributionSerializer(point_distribution_history, many=True)
        return Response(serializer.data)


class SendPoints(APIView):
    """
    Send points to team members. Date must be the current week

    Endpoint: **/v1/point/distribution/send**

    Methods: *POST PUT*

    Body:

    ```
    {
        given_points: [
          {
            to_member: "member1@email.com",
            points: 30,
            from_member: "me@me.com",
            week: "2017-01-01"
          },
          {
            to_member: email: "member2@email.com",
            points: 0,
            from_member: "me@me.com",
            week: "2017-01-01"
          }
        ],
        week: "2017-01-01"
    }
    ```
    """
    @staticmethod
    def get_or_create_point_distribution(week):
        obj, _ = PointDistribution.objects.get_or_create(week=week, is_final=False)
        return obj

    def post(self, request):
        week = request.data['week']
        if not is_current_week(week, "%Y-%m-%d"):
            raise NotCurrentWeekException()
        point_distribution = self.get_or_create_point_distribution(week)
        members_set = set(get_all_members())
        given_points = request.data['given_points']
        check_batch_includes_all_members(given_points, members_set)
        check_all_point_values_are_valid(given_points)
        serializer = PointDistributionSerializer(point_distribution, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def put(self, request):
        week = request.data['week']
        if not is_current_week(week, "%Y-%m-%d"):
            raise NotCurrentWeekException()
        given_points = request.data['given_points']
        check_all_point_values_are_valid(given_points)
        given_points_models = get_given_point_models(given_points)
        for idx, model in enumerate(given_points_models):
            serializer = GivenPointSerializer(model, data=given_points[idx])
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        point_distribution = self.get_or_create_point_distribution(week)
        serializer = PointDistributionSerializer(point_distribution)
        return Response(serializer.data)


class PointDistributionWeek(APIView):
    """
    Get a point distribution of a past week

    Endpoint: **/v1/point/distribution/YYYY-MM-DD**

    Methods: *GET*
    """
    @staticmethod
    def get_object(week):
        try:
            return PointDistribution.objects.get(week=week)
        except PointDistribution.DoesNotExist:
            raise Http404

    def get(self, request, week):
        point_distribution = self.get_object(week)
        serializer = PointDistributionSerializer(point_distribution)
        return Response(serializer.data)


class ValidateProvisionalPointDistribution(APIView):
    """
    Validate a point distribution

    Endpoint: **/v1/point/distribution/validate**

    Methods: *PUT*

    Body:

    `{"week":"YYYY-MM-DD"}`
    """
    @staticmethod
    def get_point_distribution(week):
        try:
            return PointDistribution.objects.get(week=week)
        except PointDistribution.DoesNotExist:
            raise Http404

    @staticmethod
    def get_all_members():
        try:
            return Member.objects.all()
        except Member.DoesNotExist:
            raise Http404

    def put(self, request):
        week = request.data['week']
        point_distribution = self.get_point_distribution(week)
        members_set = set(self.get_all_members())
        validate_provisional_point_distribution(point_distribution, members_set)
        point_distribution.is_final = True
        point_distribution.save()
        serializer = PointDistributionSerializer(point_distribution)
        return Response(serializer.data)
