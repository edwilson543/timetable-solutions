# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django import test
from django.db import IntegrityError

# Local application imports
from data import models


class TestLesson(test.TestCase):
    """
    Unit tests for the Break model.
    """

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "year_groups.json",
    ]

    def test_create_new_for_valid_break(self):
        """
        Test we can create a valid Break instance using create_new()
        """
        # Get some teachers and year groups to add
        teachers = models.Teacher.objects.get_all_instances_for_school(school_id=123456)
        ygs = models.YearGroup.objects.get_all_instances_for_school(school_id=123456)

        # Make the break
        break_ = models.Break.create_new(
            school_id=123456,
            break_id="1",
            break_name="Morning break",
            break_starts_at=dt.time(hour=11, minute=30),
            break_ends_at=dt.time(hour=12),
            day_of_week=models.WeekDay.MONDAY,
            teachers=teachers,
            relevant_year_groups=ygs,
        )

        # Check successful
        assert break_ in models.Break.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertQuerysetEqual(teachers, break_.teachers.all(), ordered=False)
        self.assertQuerysetEqual(ygs, break_.relevant_year_groups.all(), ordered=False)
