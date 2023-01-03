"""
Unit tests for methods on the YearGroup class
"""

# Third party imports
import pytest

# Django imports
from django import test

# Local application imports
from data import models


class TestYearGroup(test.TestCase):

    fixtures = [
        "user_school_profile.json",
    ]

    # FACTORY METHOD TESTS
    def test_create_new_valid_year_group_from_string(self):
        """
        Tests that we can create and save a YearGroup instance via the create_new method
        """
        # Execute test unit
        yg = models.YearGroup.create_new(school_id=123456, year_group="1")

        # Check outcome
        all_yg = models.YearGroup.objects.get_all_instances_for_school(school_id=123456)
        assert yg in all_yg

    def test_create_new_valid_year_group_from_integer(self):
        """
        Tests that we can create and save a YearGroup instance via the create_new method
        """
        # Execute test unit
        yg = models.YearGroup.create_new(school_id=123456, year_group=1)

        # Check outcome
        all_yg = models.YearGroup.objects.get_all_instances_for_school(school_id=123456)
        assert yg in all_yg
