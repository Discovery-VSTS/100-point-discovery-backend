import datetime
from .models import Member, PointDistribution, GivenPoint

from django.http import Http404


def is_current_week(date, pattern):
    date = datetime.datetime.strptime(date, pattern).isocalendar()[:2]
    now = datetime.datetime.now().isocalendar()[:2]
    return date == now


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


def get_given_point_models(given_points):
    models = []
    try:
        for given_point in given_points:
            from_member = given_point['from_member']
            to_member = given_point['to_member']
            week = given_point['week']
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
