from django.test import TestCase
from django.db.utils import IntegrityError


from .models import Member, PointDistribution, GivenPoint


class MemberModelTest(TestCase):
    def setUp(self):
        self.entry = Member(name="My entry title")

    def test_string_representation(self):
        self.assertEqual(str(self.entry), self.entry.email)

    def test_save(self):
        self.entry.save()


class PointDistributionTest(TestCase):
    def test_string_representation_provisional(self):
        entry = PointDistribution(week="1970-01-01", is_final=False)
        self.assertEqual(str(entry), str(entry.week) + ", provisional")

    def test_string_representation_final(self):
        entry = PointDistribution(week="1970-01-01", is_final=True)
        self.assertEqual(str(entry), str(entry.week) + ", final")

    def test_save(self):
        entry = PointDistribution(week="1970-01-01", is_final=True)
        entry.save()


class GivenPointTest(TestCase):
    def setUp(self):
        self.entry1 = Member(name="Name1", email="name1@email.com")
        self.entry2 = Member(name="Name2", email="name2@email.com")
        self.entry1.save()
        self.entry2.save()
        self.entry_point_distribution = PointDistribution(week="1970-01-01", is_final=True)
        self.entry_point_distribution.save()

    def test_string_representation(self):
        entry = GivenPoint(from_member=self.entry1, to_member=self.entry2, points=30, week="1970-01-01")
        self.assertEqual(str(entry), str(entry.week) + ", from " + str(entry.from_member) + " to " + str(entry.to_member))

    def test_save(self):
        entry = GivenPoint(from_member=self.entry1, to_member=self.entry2,
                           point_distribution=self.entry_point_distribution, points=30, week="1970-01-01")
        entry.save()

    def test_unique_together_fields(self):
        entry1 = GivenPoint(from_member=self.entry1, to_member=self.entry2,
                            point_distribution=self.entry_point_distribution, points=30, week="1970-01-01")
        entry2 = GivenPoint(from_member=self.entry1, to_member=self.entry2,
                            point_distribution=self.entry_point_distribution, points=50, week="1970-01-01")
        entry1.save()
        self.assertRaises(IntegrityError, entry2.save)
