"""
Unit tests for methods on the School model
"""

# Third party imports
import pytest

# Local application imports
from data import models
from tests import factories


@pytest.mark.django_db
class TestSchool:

    # --------------------
    # Factories tests
    # --------------------

    def test_create_new_no_access_key_given_no_schools_in_db(self):
        """
        Test that when the FIRST school is created and no access key is given,
        then one is generated automatically.
        """
        # Create a school using create_new
        school = models.School.create_new(school_name="Test")

        # Check outcome

        assert school.school_access_key == 1  # Since this is the first school

    def test_create_new_sets_access_key_to_db_school_plus_one(self):
        """
        Test that when the FIRST school is created and no access key is given,
        then one is generated automatically.
        """
        # Make a school using the factory
        factory_school = factories.School()

        # Create a school using create_new
        test_school = models.School.create_new(school_name="Test")

        # Check outcome
        assert test_school.school_access_key == factory_school.school_access_key + 1
