import datetime
import hashlib
from .models import Member, PointDistribution, GivenPoint

from django.http import Http404

DATE_PATTERN = '%Y-%m-%d'
WEEK_PATTERN = '%Y-%W'


def is_current_week(date, pattern):
    date = datetime.datetime.strptime(date, pattern).isocalendar()[:2]
    now = datetime.datetime.now().isocalendar()[:2]
    return date == now


def get_monday_from_date(date, pattern):
    date_obj = datetime.datetime.strptime(date, pattern)
    monday = date_obj - datetime.timedelta(days=date_obj.weekday())
    return monday.strftime(pattern)


def get_member(email, instance_id):
    try:
        return Member.objects.get(email=email, instance_id=instance_id)
    except Member.DoesNotExist:
        raise Http404


def get_all_members(instance_id):
    try:
        return Member.objects.filter(instance_id=instance_id)
    except Member.DoesNotExist:
        raise Http404


def get_given_point_models(given_points, week, instance_id):
    models = []
    try:
        for given_point in given_points:
            from_member = concatenate_and_hash(given_point['from_member'], instance_id)
            to_member = concatenate_and_hash(given_point['to_member'], instance_id)
            model = GivenPoint.objects.get(from_member=from_member, to_member=to_member, week=week)
            models.append(model)
    except Member.DoesNotExist:
        raise Http404

    return models


def get_points_distributions(week):
    try:
        return PointDistribution.objects.get(week=week)
    except PointDistribution.DoesNotExist:
        raise Http404


def filter_final_points_distributions(instance_id, is_final=True):
    try:
        return PointDistribution.objects.filter(instance_id=instance_id, is_final=is_final)
    except PointDistribution.DoesNotExist:
        raise Http404


def concatenate_and_hash(field1, field2):
    concat_str = '%s%s' % (field1, field2)
    hashed_obj = hashlib.md5(concat_str.encode('utf-8'))
    return hashed_obj.hexdigest()
