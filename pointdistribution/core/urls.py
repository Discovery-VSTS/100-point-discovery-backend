from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'members/$', views.MemberList.as_view()),
    url(r'points/distribution/$', views.PointDistributionEndpoint.as_view()),
    url(r'points/distribution/(?P<week>\d{4}-\d{2}-\d{2})/$', views.PointDistributionWeek.as_view()),
    url(r'points/distribution/history/$', views.PointDistributionHistory.as_view()),
]
