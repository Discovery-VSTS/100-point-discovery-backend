from .models import Member, GivenPoint, GivenPointArchived, PointDistribution
from .serializers import MemberSerializer, GivenPointArchivedSerializer, PointDistributionSerializer
from .points_operation import validate_provisional_point_distribution, check_point_distribution_includes_all_members, \
    check_all_point_values_are_valid
from .utils import is_current_week, get_member, filter_final_points_distributions, get_all_members
from .exceptions import NotCurrentWeekException

from django.http import Http404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response


class MemberList(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class MemberPointsHistory(APIView):
    @staticmethod
    def get_given_points_member(member):
        try:
            return GivenPointArchived.objects.filter(from_member=member)
        except GivenPointArchived.DoesNotExist:
            raise Http404

    def get(self, request, email):
        member = get_member(email)
        given_points = self.get_given_points_member(member)
        serializer = GivenPointArchivedSerializer(given_points, many=True)
        return Response(serializer.data)


class PointDistributionHistory(APIView):
    def get(self, request):
        point_distribution_history = filter_final_points_distributions()
        serializer = PointDistributionSerializer(point_distribution_history, many=True)
        return Response(serializer.data)


class SendPoints(APIView):
    @staticmethod
    def get_or_create_point_distribution(week):
        obj, _ = PointDistribution.objects.get_or_create(week=week, is_final=False)
        return obj


    def post(self, request):
        week = request.data['week']
        if not is_current_week(week, "%Y-%m-%d"):
            raise NotCurrentWeekException()
        point_distribution = self.get_or_create_point_distribution(week)
        members_set = {get_all_members()}
        check_point_distribution_includes_all_members(point_distribution, members_set)
        check_all_point_values_are_valid(point_distribution)
        serializer = PointDistributionSerializer(point_distribution, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def put(self, request):
        week = request.data['week']
        if not is_current_week(week, "%Y-%m-%d"):
            raise NotCurrentWeekException()
        point_distribution = self.get_or_create_point_distribution(week)
        check_all_point_values_are_valid(point_distribution)
        serializer = PointDistributionSerializer(point_distribution, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class PointDistributionWeek(APIView):
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
        members_list = self.get_all_members()
        validate_provisional_point_distribution(point_distribution, members_list)
        point_distribution.is_final = True
        point_distribution.save()
        serializer = PointDistributionSerializer(point_distribution)
        return Response(serializer.data)
