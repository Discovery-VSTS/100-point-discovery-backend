from django.test import TestCase


from .models import Member


class MemberModelTest(TestCase):
    def test_string_representation(self):
        entry = Member(name="My entry title")
        self.assertEqual(str(entry), entry.name)
