from django.contrib import admin
from .models import GivenPoint, GivenPointArchived, Member, PointDistribution


admin.site.register(GivenPoint)
admin.site.register(GivenPointArchived)
admin.site.register(Member)
admin.site.register(PointDistribution)
