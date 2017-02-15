import datetime


def is_current_week(date, pattern):
    date = datetime.datetime.strptime(date, pattern).isocalendar()[:2]
    now = datetime.datetime.now().isocalendar()[:2]
    return date == now
