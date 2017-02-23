import datetime
from .models import Member, PointDistribution

from django.http import Http404


def is_current_week(date, pattern):
    date = datetime.datetime.strptime(date, pattern).isocalendar()[:2]
    now = datetime.datetime.now().isocalendar()[:2]
    return date == now


def get_member(email):
    try:
        return Member.objects.get(email=email)
    except Member.DoesNotExist:
        raise Http404


def get_all_members():
    try:
        return Member.objects.all()
    except Member.DoesNotExist:
        raise Http404


def get_points_distributions(week):
    try:
        return PointDistribution.objects.get(week=week)
    except PointDistribution.DoesNotExist:
        raise Http404


def filter_final_points_distributions(is_final=True):
    try:
        return PointDistribution.objects.filter(is_final=is_final)
    except PointDistribution.DoesNotExist:
        raise Http404
