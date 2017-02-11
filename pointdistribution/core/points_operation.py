from .exceptions import RepeatedPointValueException, MembersMissingException, InvalidSumPointsException, \
    ConflictInPointsToMemberException


def validate_provisional_point_distribution(point_distribution, members_list):
    member_to_point = {}
    point_to_member = {}
    given_points = point_distribution.given_points.all()
    for given_point in given_points:
        points = given_point.points
        to_member = given_point.to_member.__str__()
        if to_member in member_to_point and member_to_point[to_member] != points:
            raise ConflictInPointsToMemberException()
        member_to_point[to_member] = points
        if points in point_to_member:
            raise RepeatedPointValueException()
        point_to_member[points] = to_member
    if len(member_to_point) != len(members_list):
        raise MembersMissingException()
    sum_points = 0
    for member, points in member_to_point.items():
        sum_points += points
    if sum_points != 100:
        raise InvalidSumPointsException()
