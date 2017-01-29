from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(primary_key=True, max_length=30)

    def __str__(self):
        return self.name.__str__()


class GivenPoint(models.Model):
    toMember = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_toMember")
    points = models.IntegerField()
    fromMember = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_fromMember")
    week = models.DateField()
    is_provisional = models.BooleanField()

    class Meta:
        unique_together = ('toMember', 'points', 'fromMember')


class PointDistribution(models.Model):
    GivenPoints = models.ManyToManyField(GivenPoint)
    week = models.DateField()