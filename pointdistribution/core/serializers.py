from rest_framework import serializers

from .models import Member, GivenPoint, PointDistribution


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('name', 'email')


class GivenPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = GivenPoint
        fields = ('to_member', 'points', 'from_member', 'week')


class PointDistributionSerializer(serializers.ModelSerializer):
    given_points = GivenPointSerializer(many=True)

    class Meta:
        model = PointDistribution
        fields = ('given_points', 'week', 'is_final')

    def create(self, validated_data):
        given_points_data = validated_data.pop('given_points')
        point_distribution = PointDistribution.objects.create(**validated_data)
        for given_point_data in given_points_data:
            GivenPoint.objects.create(point_distribution=point_distribution, **given_point_data)
        return point_distribution
