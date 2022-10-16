"""Unit tests for the utility functions in the domain layer"""

# Standard library imports
import datetime as dt

# Django imports
from django import test

# Local application imports
from domain import utils


class TestUtils(test.TestCase):
    fixtures = ["user_school_profile.json", "timetable.json"]

    def test_get_user_timeslots(self):
        """
        Test that the correct set of timeslots, and the correct ordering, is returned by get_user_timeslots
        """
        # Set test parameters
        school_access_key = 123456
        expected_times = [dt.time(hour=9 + x) for x in range(0, 7)]  # Fixture has 9:00, 10:00, ... , 15:00

        # Execute test unit
        timeslots = utils.get_user_timetable_slots(school_access_key=school_access_key)

        # Check outcome
        assert timeslots == expected_times
