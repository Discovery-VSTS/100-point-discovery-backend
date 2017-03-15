from django.test import TestCase
from django.db.utils import IntegrityError
from rest_framework.test import APIRequestFactory
from datetime import date
import datetime
from unittest import skip

from .models import Member, PointDistribution, GivenPoint, GivenPointArchived
from .views import PointDistributionHistory, PointDistributionWeek, MemberList, SendPoints, \
    ValidateProvisionalPointDistribution

# TEST MODELS


class MemberModelTest(TestCase):
    def setUp(self):
        self.entry = Member(name="My entry title", instance_id="1234")

    def test_string_representation(self):
        self.assertEqual(str(self.entry), self.entry.email + "/" + self.entry.instance_id)

    def test_save(self):
        self.entry.save()


class PointDistributionTest(TestCase):
    def test_string_representation_provisional(self):
        entry = PointDistribution(week="1970-01-01", date="1970-01-01", is_final=False, instance_id="1234")
        self.assertEqual(str(entry), str(entry.week) + ", provisional")
        entry = PointDistribution(week="1970-01-01", date="1970-01-01", is_final=True, instance_id="1234")
        self.assertEqual(str(entry), str(entry.week) + ", final")

    def test_save(self):
        entry = PointDistribution(week="1970-01-01", date="1970-01-01", is_final=True)
        entry.save()


class GivenPointTest(TestCase):
    def setUp(self):
        self.entry1 = Member(name="Name1", email="name1@email.com", instance_id="1234",
                             identifier="82e37e019472168a59a6d959936e6aa7")
        self.entry2 = Member(name="Name2", email="name2@email.com", instance_id="1234",
                             identifier="67917aabb3bf89714230616525ea5632")
        self.entry1.save()
        self.entry2.save()
        self.entry_point_distribution = PointDistribution(week="1970-01-01", date="1970-01-01", is_final=True,
                                                          instance_id="1234")
        self.entry_point_distribution.save()

    def test_string_representation(self):
        entry = GivenPoint(from_member=self.entry1, to_member=self.entry2, points=30, week="1970-01-01",
                           instance_id="1234")
        self.assertEqual(str(entry), str(entry.week) + ", from " + str(entry.from_member) + " to " + str(entry.to_member))

    def test_save(self):
        entry = GivenPoint(from_member=self.entry1, to_member=self.entry2,
                           point_distribution=self.entry_point_distribution, points=30, week="1970-01-01",
                           instance_id="1234")
        entry.save()

    def test_unique_together_fields(self):
        entry1 = GivenPoint(from_member=self.entry1, to_member=self.entry2,
                            point_distribution=self.entry_point_distribution, points=30, week="1970-01-01",
                            instance_id="1234")
        entry2 = GivenPoint(from_member=self.entry1, to_member=self.entry2,
                            point_distribution=self.entry_point_distribution, points=50, week="1970-01-01",
                            instance_id="1234")
        entry1.save()
        self.assertRaises(IntegrityError, entry2.save)

# TEST VIEWS


class MemberListTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @skip('Need to mock returned request')
    def test_full_history(self):
        self.entry1 = Member(name="Name1", email="name1@email.com", instance_id="1234",
                             identifier="82e37e019472168a59a6d959936e6aa7")
        self.entry2 = Member(name="Name2", email="name2@email.com", instance_id="1234",
                             identifier="67917aabb3bf89714230616525ea5632")
        self.entry1.save()
        self.entry2.save()
        request = self.factory.get('/v1/members/?instance_id=1234')
        response = MemberList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"name": "Name1", "email": "name1@email.com", "instance_id": "1234",
                                          "identifier": "82e37e019472168a59a6d959936e6aa7"},
                                         {"name": "Name2", "email": "name2@email.com", "instance_id": "1234",
                                          "identifier": "67917aabb3bf89714230616525ea5632"}])

    def test_create_member(self):
        request = self.factory.post('/v1/members/', {"name": "Name", "email": "name@email.com", "instance_id": "1234"})
        response = MemberList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"name": "Name", "email": "name@email.com", "instance_id": "1234",
                                         "identifier": "70eef677b6c2f6e45bb577cf362b069f"})


class PointDistributionHistoryTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_empty_history(self):
        request = self.factory.get('/v1/points/distribution/history/?instance=1234')
        response = PointDistributionHistory.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


class SendPointsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.entry1 = Member(name="Name1", email="name1@email.com", instance_id="1234",
                             identifier="82e37e019472168a59a6d959936e6aa7")
        self.entry2 = Member(name="Name2", email="name2@email.com", instance_id="1234",
                             identifier="67917aabb3bf89714230616525ea5632")
        self.entry1.save()
        self.entry2.save()
        self.today = date.today().isoformat()

    @skip("Response data is not a fully parsed JSON object")
    def test_post(self):
        distr = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 0,
                    'week': self.today,
                    'instance_id': '1234'
                },
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name2@email.com',
                    'points': 100,
                    'week': self.today,
                    'instance_id': '1234'
                }
            ],
            'week': self.today,
            'instance_id': '1234'
        }
        request = self.factory.post('/v1/points/distribution/send/', distr, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        distr['is_final'] = False
        print(response.data)
        print(distr)
        self.assertEqual(response.data, distr)

    @skip("Response data is not a fully parsed JSON object")
    def test_put(self):
        distr = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 0,
                    'week': self.today,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name2@email.com',
                    'points': 100,
                    'week': self.today,
                    'instance_id': "1234"
                }
            ],
            'week': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        distr2 = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 50,
                    'week': self.today,
                    'instance_id': "1234"
                }
            ],
            'week': self.today,
            'instance_id': "1234"
        }
        request = self.factory.put('/v1/points/distribution/send/', distr2, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        distr['given_points'][0]['points'] = 50
        distr['is_final'] = False
        self.assertEqual(response.data, distr)

    def test_post_not_all_members_should_return_400(self):
        distr = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 0,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'detail': "Some members haven't been graded yet"})


class PointDistributionWeekTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.entry1 = Member(name="Name1", email="name1@email.com", instance_id="1234",
                             identifier="82e37e019472168a59a6d959936e6aa7")
        self.entry1.save()
        self.today = date.today().isoformat()
        self.monday = date.today() - datetime.timedelta(days=date.today().weekday())

    @skip("Base json not well formatted")
    def test_point_distribution(self):
        distr = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 0,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request = self.factory.get('/v1/points/distribution/%s/?instance_id=1234' % self.monday)
        response = PointDistributionWeek.as_view()(request, week=self.monday)
        self.assertEqual(response.status_code, 200)
        distr['is_final'] = False
        distr['week'] = self.monday.strftime('%Y-%m-%d')
        self.assertEqual(response.data, distr)

    def test_point_distribution_non_existant(self):
        request = self.factory.get('/v1/points/distribution/%s/?instance_id=1234' % self.today)
        response = PointDistributionWeek.as_view()(request, week=self.today)
        self.assertEqual(response.status_code, 404)


class ValidateProvisionalPointDistributionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.entry1 = Member(name="Name1", email="name1@email.com", instance_id="1234",
                             identifier="82e37e019472168a59a6d959936e6aa7")
        self.entry2 = Member(name="Name2", email="name2@email.com", instance_id="1234",
                             identifier="67917aabb3bf89714230616525ea5632")
        self.entry1.save()
        self.entry2.save()
        self.today = date.today().isoformat()
        self.monday = date.today() - datetime.timedelta(days=date.today().weekday())

    def test_valid_point_distribution(self):
        distr1 = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 51,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name2@email.com',
                    'points': 49,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr1, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        distr2 = {
            'given_points': [
                {
                    'from_member': 'name2@email.com',
                    'to_member': 'name1@email.com',
                    'points': 51,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name2@email.com',
                    'to_member': 'name2@email.com',
                    'points': 49,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr2, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request = self.factory.put('/v1/points/distribution/send/', {'week': self.monday, 'instance_id': '1234'})
        response = ValidateProvisionalPointDistribution.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_final'], True)
        self.assertEqual(len(response.data['given_points']), 2)
        self.assertEqual(response.data['given_points'][0]['from_member'], None)
        self.assertEqual(response.data['given_points'][1]['from_member'], None)
        self.assertEqual(len(GivenPointArchived.objects.all()), 4)

    def test_points_between_members_dont_match(self):
        distr1 = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 51,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name2@email.com',
                    'points': 49,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr1, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        distr2 = {
            'given_points': [
                {
                    'from_member': 'name2@email.com',
                    'to_member': 'name1@email.com',
                    'points': 0,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name2@email.com',
                    'to_member': 'name2@email.com',
                    'points': 49,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr2, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request = self.factory.put('/v1/points/distribution/send/', {'week': self.monday, 'instance_id': '1234'})
        response = ValidateProvisionalPointDistribution.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data,
                         {'detail': 'There is a conflict of points with at lest one member in the group'})

    def test_points_dont_add_up_to_100(self):
        distr1 = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 51,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name2@email.com',
                    'points': 10,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr1, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        distr2 = {
            'given_points': [
                {
                    'from_member': 'name2@email.com',
                    'to_member': 'name1@email.com',
                    'points': 51,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name2@email.com',
                    'to_member': 'name2@email.com',
                    'points': 10,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr2, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request = self.factory.put('/v1/points/distribution/send/', {'week': self.monday, 'instance_id': '1234'})
        response = ValidateProvisionalPointDistribution.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'detail': 'Sum of points different than 100'})

    def test_repeated_points(self):
        distr1 = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 50,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name2@email.com',
                    'points': 50,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr1, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        distr2 = {
            'given_points': [
                {
                    'from_member': 'name2@email.com',
                    'to_member': 'name1@email.com',
                    'points': 50,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name2@email.com',
                    'to_member': 'name2@email.com',
                    'points': 50,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr2, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request = self.factory.put('/v1/points/distribution/send/', {'week': self.monday, 'instance_id': '1234'})
        response = ValidateProvisionalPointDistribution.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'detail': 'Several team members have the same amount of points'})

    def test_not_all_members_gave_points(self):
        distr1 = {
            'given_points': [
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name1@email.com',
                    'points': 51,
                    'instance_id': "1234"
                },
                {
                    'from_member': 'name1@email.com',
                    'to_member': 'name2@email.com',
                    'points': 49,
                    'instance_id': "1234"
                }
            ],
            'date': self.today,
            'instance_id': "1234"
        }
        request = self.factory.post('/v1/points/distribution/send/', distr1, format='json')
        response = SendPoints.as_view()(request)
        self.assertEqual(response.status_code, 200)
        request = self.factory.put('/v1/points/distribution/send/', {'week': self.monday, 'instance_id': '1234'})
        response = ValidateProvisionalPointDistribution.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'detail': "Not all members gave points to their colleagues"})
