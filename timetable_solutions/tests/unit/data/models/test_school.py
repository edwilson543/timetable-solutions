"""
Unit tests for methods on the School model
"""

# Django imports
from django import test

# Local application imports
from data import models


class TestClassroom(test.TestCase):

    fixtures = ["user_school_profile.json"]

    # FACTORY METHOD TESTS
    def test_create_new_no_access_key_given(self):
        """
        Test that when a school is created and no access key is given, then one is generated automatically.
        """
        # Execute test unit
        school = models.School.create_new(school_name="Test")

        # Check outcome
        assert school.school_access_key == 123457  # Since the max access key in the fixture is 123456

    # MISCELLANEOUS METHOD TESTS
    def test_get_new_access_key_equals_fixture_access_key_plus_one(self):
        """
        There is one school the fixtures with access key 123456, so we expect the next available access key to be
        123457
        """
        # Execute test unit
        new_access_key = models.School.get_new_access_key()

        # Check outcome
        assert new_access_key == 123457
