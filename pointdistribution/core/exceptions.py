from rest_framework.exceptions import APIException


class RepeatedPointValueException(APIException):
    status_code = 400
    default_detail = "Several team members have the same amount of points"
    default_code = 'bad_request'


class MembersMissingException(APIException):
    status_code = 400
    default_detail = "Some members haven't been graded yet"
    default_code = 'bad_request'


class InvalidSumPointsException(APIException):
    status_code = 400
    default_detail = "Sum of points different than 100"
    default_code = 'bad_request'


class ConflictInPointsToMemberException(APIException):
    status_code = 400
    default_detail = "There is a conflict of points with at lest one member in the group"
    default_code = 'bad_request'


class NotCurrentWeekException(APIException):
    status_code = 400
    default_detail = "This operation can not be performed at this year and week"
    default_code = 'bad_request'


class InvalidOrRepeatedMemberException(APIException):
    status_code = 400
    default_detail = "A member is invalid or has received points twice"
    default_code = 'bad_request'
