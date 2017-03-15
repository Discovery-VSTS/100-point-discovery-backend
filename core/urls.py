from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'members/$', views.MemberList.as_view()),
    url(r'members/reset/$', views.reset_database),
    url(r'member/history/(?P<email>.+)/$', views.MemberPointsHistory.as_view()),
    url(r'points/distribution/(?P<week>\d{4}-\d{2}-\d{2})/$', views.PointDistributionWeek.as_view()),
    url(r'points/distribution/send/$', views.SendPoints.as_view()),
    url(r'points/distribution/validate/$', views.ValidateProvisionalPointDistribution.as_view()),
    url(r'points/distribution/history/$', views.PointDistributionHistory.as_view()),
]
