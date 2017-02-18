from .exceptions import RepeatedPointValueException, MembersMissingException, InvalidSumPointsException, \
    ConflictInPointsToMemberException, InvalidOrRepeatedMemberException, PointValueNotValidException
from .models import GivenPoint


def normalize_point_distribution(point_distribution, members_list):
    given_points = point_distribution.given_points.all()
    week = point_distribution.week
    member_to_point = {}
    n_from_members = {}
    for given_point in given_points:
        points = given_point.points
        to_member = given_point.to_member
        member_to_point[to_member] = (member_to_point[to_member]+points if to_member in member_to_point else points)
        n_from_members[to_member] = (n_from_members[to_member]+1 if to_member in n_from_members else 1)
    if len(member_to_point) != len(members_list):
        raise MembersMissingException()
    normalized_given_points = []
    for member, points in member_to_point.items():
        normalized_points = points//n_from_members[member]
        normalized_given_points.append(GivenPoint(to_member=member, points=normalized_points,
                                                  point_distribution=point_distribution, week=week))
    for given_point in given_points:
        given_point.delete()
    for normalized_given_point in normalized_given_points:
        normalized_given_point.save()


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


def check_point_distribution_includes_all_members(point_distribution, members_set):
    given_points = point_distribution.given_points.all()
    for given_point in given_points:
        member = given_point.to_member
        if member in members_set:
            members_set.remove(member)
        else:
            raise InvalidOrRepeatedMemberException()
    if len(members_set) > 0:
        raise MembersMissingException()


def check_all_point_values_are_valid(point_distribution):
    given_points = point_distribution.given_points.all()
    for given_point in given_points:
        points = given_point.points
        if points > 100 or points < 0:
            raise PointValueNotValidException()
