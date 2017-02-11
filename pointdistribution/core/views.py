from .models import Member, GivenPoint, PointDistribution
from .serializers import MemberSerializer, GivenPointSerializer, PointDistributionSerializer
from .points_operation import validate_provisional_point_distribution, normalize_point_distribution
from .utils import is_current_week
from .exceptions import NotCurrentWeekException

from django.http import Http404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response


class MemberList(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class PointDistributionHistory(APIView):
    @staticmethod
    def get_object():
        try:
            return PointDistribution.objects.filter(is_final=True)
        except PointDistribution.DoesNotExist:
            raise Http404

    def get(self, request):
        point_distribution_history = self.get_object()
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


class NormalizePointDistribution(APIView):
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
        normalize_point_distribution(point_distribution, members_list)
        point_distribution = self.get_point_distribution(week)
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
