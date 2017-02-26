from rest_framework import serializers

from .models import Member, GivenPoint, GivenPointArchived, PointDistribution


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('name', 'email')


class GivenPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = GivenPoint
        fields = ('to_member', 'points', 'from_member', 'week')

    def create(self, validated_data):
        given_point = GivenPoint.objects.create(**validated_data)
        return given_point

    def update(self, instance, validated_data):
        instance.points = validated_data.get('points', instance.points)
        instance.save()
        return instance


class GivenPointArchivedSerializer(serializers.ModelSerializer):
    from_member = MemberSerializer()
    to_member = MemberSerializer()

    class Meta:
        model = GivenPointArchived
        fields = ('from_member', 'to_member', 'points', 'week')

    def create(self, validated_data):
        given_point = GivenPointArchived.objects.create(**validated_data)
        return given_point


class PointDistributionSerializer(serializers.ModelSerializer):
    given_points = GivenPointSerializer(many=True)

    class Meta:
        model = PointDistribution
        fields = ('given_points', 'week', 'is_final')

    def update(self, instance, validated_data):
        given_points_data = validated_data.pop('given_points')
        for given_point_data in given_points_data:
            GivenPoint.objects.create(point_distribution=instance, **given_point_data)
        instance.save()
        return instance
