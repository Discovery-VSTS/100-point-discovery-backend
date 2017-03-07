from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(primary_key=True, max_length=30)
    instance_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ('email', 'instance_id')

    def __str__(self):
        return self.email.__str__()


class PointDistribution(models.Model):
    week = models.DateField(primary_key=True)
    is_final = models.BooleanField()
    instance_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ('week', 'instance_id')

    def __str__(self):
        return self.week.__str__() + ", " + ("final" if self.is_final else "provisional")


class GivenPoint(models.Model):
    from_member = models.ForeignKey(Member, blank=True, null=True, on_delete=models.CASCADE,
                                    related_name="%(app_label)s_%(class)s_fromMember")
    to_member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_toMember")
    points = models.IntegerField()
    point_distribution = models.ForeignKey(PointDistribution, on_delete=models.CASCADE, related_name="given_points")
    week = models.DateField()
    instance_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ('to_member', 'week', 'from_member', 'instance_id')

    def __str__(self):
        return self.week.__str__() + ", from " + self.from_member.__str__() + " to " + self.to_member.__str__()


class GivenPointArchived(models.Model):
    from_member = models.ForeignKey(Member, blank=True, null=True, on_delete=models.CASCADE,
                                    related_name="%(app_label)s_%(class)s_fromMember")
    to_member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_toMember")
    points = models.IntegerField()
    week = models.DateField()
    instance_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ('to_member', 'week', 'from_member', 'instance_id')
