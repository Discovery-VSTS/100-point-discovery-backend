from django.test import TestCase
from django.db.utils import IntegrityError
from rest_framework.test import APIRequestFactory


from .models import Member, PointDistribution, GivenPoint
from .views import PointDistributionHistory, MemberList

# TEST MODELS


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

# TEST VIEWS


class MemberListTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_full_history(self):
        self.entry1 = Member(name="Name1", email="name1@email.com")
        self.entry2 = Member(name="Name2", email="name2@email.com")
        self.entry1.save()
        self.entry2.save()
        request = self.factory.get('/core/members/')
        response = MemberList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"name": "Name1", "email": "name1@email.com"},
                                         {"name": "Name2", "email": "name2@email.com"}])

    def test_create_member(self):
        request = self.factory.post('/core/members/', {"name": "Name", "email": "name@email.com"})
        response = MemberList.as_view()(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"name": "Name", "email": "name@email.com"})


class PointDistributionHistoryTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_empty_history(self):
        request = self.factory.get('/core/points/distribution/history/')
        response = PointDistributionHistory.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
