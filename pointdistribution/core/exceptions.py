from rest_framework.exceptions import APIException


class RepeatedPointValueException(APIException):
    status_code = 400
    default_detail = "Several team members have the same amount of points"
    default_code = 'bad_request'


class MembersMissingException(APIException):
    status_code = 400
    default_detail = "Some members haven't been graded yet"
    default_code = 'bad_request'


class NotAllMembersGavePointsException(APIException):
    status_code = 400
    default_detail = "Not all members gave points to their colleagues"
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


class PointValueNotValidException(APIException):
    status_code = 400
    default_detail = "One of the given points exceeds 100 or contains a negative number"
    default_code = 'bad_request'


class InvalidGivenPointsArchivedData(APIException):
    status_code = 400
    default_detail = "The data of a given point is malformed"
    default_code = 'bad_request'
