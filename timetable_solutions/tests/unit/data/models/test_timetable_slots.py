"""
Unit tests for methods on the TimetableSlot and TimetableSlotQuerySet class
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django import test
from django.db import IntegrityError

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


class TestTimetableSlot(test.TestCase):
    """Unit tests for the TimetableSlot model"""
    fixtures = ["user_school_profile.json", "timetable.json"]

    # FACTORY METHOD TESTS
    def test_create_new_valid_timeslot(self):
        """
        Tests that we can create and save a TimetableSlot via the create_new method
        """
        # Execute test unit
        slot = models.TimetableSlot.create_new(school_id=123456, slot_id=100, day_of_week=1,  # Slot 100 available
                                               period_starts_at=dt.time(hour=9), period_duration=dt.timedelta(hours=1))

        # Check outcome
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)
        assert slot in all_slots

    def test_create_new_fails_when_timetable_slot_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Timetable slots with the same id / school, due to unique_together on the
        Meta class.
        """
        # Execute test unit
        with pytest.raises(IntegrityError):
            models.TimetableSlot.create_new(
                school_id=123456, slot_id=1,  # Note that slot 1 is already taken
                day_of_week=1, period_starts_at=dt.time(hour=9), period_duration=dt.timedelta(hours=1))

    def test_create_new_fails_with_invalid_day_of_week(self):
        """
        Tests that we can cannot create two Timetable slots with the same id / school, due to unique_together on the
        Meta class.
        """
        # Execute test unit
        with pytest.raises(ValueError):
            models.TimetableSlot.create_new(
                school_id=123456, slot_id=100,  # Note that slot 100 is available
                day_of_week=100,  # Invalid day of week
                period_starts_at=dt.time(hour=9), period_duration=dt.timedelta(hours=1))

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all timetable slots associated with a school
        """
        # Execute test unit
        outcome = models.TimetableSlot.delete_all_instances_for_school(school_id=123456)

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.TimetableSlot"] == 35

        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)
        assert all_slots.count() == 0

    # QUERY METHOD TESTS
    def test_get_timeslots_on_given_day(self):
        """Test that filtering timeslots by school and day to get the slot ids is working as expected"""
        # Test parameters
        monday = models.WeekDay.MONDAY.value

        # Execute test unit
        slots = models.TimetableSlot.get_timeslot_ids_on_given_day(school_id=123456, day_of_week=monday)

        # Check outcome
        assert set(slots) == {1, 6, 11, 16, 21, 26, 31}

    def test_get_unique_start_times(self):
        """
        Test that the correct set of timeslots, and the correct ordering, is returned by get_unique_start_times
        """
        # Set test parameters
        school_access_key = 123456
        expected_times = [dt.time(hour=9 + x) for x in range(0, 7)]  # Fixture has 9:00, 10:00, ... , 15:00

        # Execute test unit
        timeslots = models.TimetableSlot.get_unique_start_times(school_id=school_access_key)

        # Check outcome
        assert timeslots == expected_times
