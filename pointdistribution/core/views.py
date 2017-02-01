from .models import Member, GivenPoint, PointDistribution
from .serializers import MemberSerializer, GivenPointSerializer, PointDistributionSerializer

from django.http import Http404

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response


class MemberList(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class PointDistributionEndpoint(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = PointDistribution.objects.all()
    serializer_class = PointDistributionSerializer


class PointDistributionHistory(APIView):
    def get_object(self):
        try:
            return PointDistribution.objects.filter(is_final=True)
        except PointDistribution.DoesNotExist:
            raise Http404

    def get(self, request):
        point_distribution_history = self.get_object()
        serializer = PointDistributionSerializer(point_distribution_history, many=True)
        return Response(serializer.data)


class PointDistributionWeek(APIView):
    def get_object(self, week):
        try:
            return PointDistribution.objects.get(week=week)
        except PointDistribution.DoesNotExist:
            raise Http404

    def get(self, request, week):
        point_distribution = self.get_object(week)
        serializer = PointDistributionSerializer(point_distribution)
        return Response(serializer.data)
