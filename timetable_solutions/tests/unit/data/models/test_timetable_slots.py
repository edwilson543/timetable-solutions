"""
Unit tests for methods on the TimetableSlot and TimetableSlotQuerySet class
"""
# Django imports
from django import test

# Local application imports
from data import models


class TestTimetableSlotQuerySet(test.TestCase):
    """Unit tests for the TimetableSlot QuerySet"""
    fixtures = ["user_school_profile.json", "timetable.json"]

    def test_get_timeslots_on_given_day(self):
        """Test that filtering timeslots by school and day is working as expected"""
        # Test parameters
        monday = models.WeekDay.MONDAY.value

        # Execute test unit
        slots = models.TimetableSlot.objects.get_timeslots_on_given_day(school_id=123456, day_of_week=monday)

        # Check outcome
        assert slots.count() == 7