from .exceptions import RepeatedPointValueException, MembersMissingException, InvalidSumPointsException, \
    ConflictInPointsToMemberException, InvalidOrRepeatedMemberException, PointValueNotValidException
from .models import GivenPoint
from .serializers import GivenPointArchivedSerializer
from .exceptions import InvalidGivenPointsArchivedData
from django.forms.models import model_to_dict


def validate_provisional_point_distribution(point_distribution, members_list):
    member_to_point = {}
    point_to_member = {}
    given_points = point_distribution.given_points.all()
    for given_point in given_points:
        points = given_point.points
        to_member = given_point.to_member
        if to_member in member_to_point and member_to_point[to_member] != points:
            raise ConflictInPointsToMemberException()
        member_to_point[to_member] = points
        if points in point_to_member and point_to_member[points] != to_member:
            raise RepeatedPointValueException()
        point_to_member[points] = to_member
    if len(member_to_point) != len(members_list):
        raise MembersMissingException()
    for given_point in given_points:
        given_point_dict = model_to_dict(given_point)
        del given_point_dict['point_distribution']
        del given_point_dict['id']
        serializer = GivenPointArchivedSerializer(data=given_point_dict)
        if not serializer.is_valid():
            raise InvalidGivenPointsArchivedData()
        serializer.save()
        given_point.delete()
    sum_points = 0
    week = point_distribution.week
    for member, points in member_to_point.items():
        new_given_point_entry = GivenPoint(to_member=member, points=points,
                                           point_distribution=point_distribution, week=week)
        new_given_point_entry.save()
        sum_points += points
    if sum_points != 100:
        raise InvalidSumPointsException()


def check_batch_includes_all_members(given_points, members_set):
    for given_point in given_points:
        member = given_point['to_member']
        if member in members_set:
            members_set.remove(member)
        else:
            raise InvalidOrRepeatedMemberException()
    if len(members_set) > 0:
        raise MembersMissingException()


def check_all_point_values_are_valid(given_points):
    for given_point in given_points:
        points = given_point['points']
        if points > 100 or points < 0:
            raise PointValueNotValidException()
