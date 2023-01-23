"""
Unit tests for methods on the TimetableSlot and TimetableSlotQuerySet class
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.core import exceptions
from django.db import IntegrityError

# Local application imports
from data import constants
from data import models
from tests import data_factories


@pytest.mark.django_db
class TestTimetableSlotQuerySet:
    """Unit tests for the TimetableSlot QuerySet"""

    def test_get_timeslots_on_given_day_year_one(self):
        """
        Test that filtering timeslots by school and day is working as expected.
        In particular that only the year groups relevant to year 1 are returned.
        """
        # Make a year group with a slot on monday
        school = factories.School()
        yg = factories.YearGroup(school=school)
        slot = factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            day_of_week=constants.Day.MONDAY,
        )

        # Make some dummy slots that we don't expect in the outcome
        factories.TimetableSlot()  # Dummy slot at different school
        factories.TimetableSlot(
            school=school,
            day_of_week=constants.Day.TUESDAY,  # Dummy slot on different day
        )
        factories.TimetableSlot(  # Dummy slot not for this year group
            school=school,
            day_of_week=constants.Day.MONDAY,
        )

        # Get slots and check only 1 was retrieved
        slots = models.TimetableSlot.objects.get_timeslots_on_given_day(
            school_id=school.school_access_key,
            day_of_week=slot.day_of_week,
            year_group=yg,
        )

        assert slots.count() == 1
        assert slot in slots
        # Therefore we have that none of the dummy slots were in the result

    @pytest.mark.parametrize("n_expected_clashes", [1, 2, 3])
    def test_filter_for_clashes_expecting_clashes(self, n_expected_clashes):
        """
        Test that a queryset of three clashes is returned for a slot clashing with 3 slots in total
        (including itself).
        """
        school = factories.School()
        monday = constants.Day.MONDAY

        # Make the following slots: 8:30-9:30; 9:00-10:00; 9:30-10:30, 10:00-11:00
        if n_expected_clashes > 1:
            clash_slot_1 = factories.TimetableSlot(
                school=school,
                day_of_week=monday,
                period_starts_at=dt.time(hour=8, minute=30),
                period_ends_at=dt.time(hour=9, minute=30),
            )
            if n_expected_clashes > 2:
                clash_slot_2 = factories.TimetableSlot.get_next_consecutive_slot(
                    clash_slot_1
                )

        check_slot = factories.TimetableSlot(
            school=school,
            day_of_week=monday,
            period_starts_at=dt.time(hour=9),
            period_ends_at=dt.time(hour=10),
        )
        # This slot shouldn't appear in the clashes
        factories.TimetableSlot.get_next_consecutive_slot(check_slot)

        # Get the clashes and check just 3
        clashes = models.TimetableSlot.objects.filter_for_clashes(check_slot)

        # Check just 3 clashes
        assert clashes.count() == n_expected_clashes

        assert check_slot in clashes

        if n_expected_clashes > 1:
            assert clash_slot_1 in clashes
        if n_expected_clashes > 2:
            assert clash_slot_2 in clashes
        # Therefore we have that the 9:00-10:00 slot was not a clash


@pytest.mark.django_db
class TestTimetableSlot:
    """Unit tests for the TimetableSlot model"""

    # --------------------
    # Factories tests
    # --------------------

    def test_create_new_valid_timeslot(self):
        """
        Tests that we can create and save a TimetableSlot via the create_new method
        """
        # Make a school and year group for the timetable slot
        school = factories.School()
        yg = factories.YearGroup(school=school)

        # Make a slot at the school
        slot = models.TimetableSlot.create_new(
            school_id=school.school_access_key,
            slot_id=1,
            day_of_week=constants.Day.MONDAY,
            period_starts_at=dt.time(hour=9),
            period_ends_at=dt.time(hour=10),
            relevant_year_groups=models.YearGroup.objects.all(),
        )

        # Check slot saved to db and defined as expected
        all_slots = models.TimetableSlot.objects.all()
        assert all_slots.count() == 1
        assert all_slots.first() == slot

        all_ygs = slot.relevant_year_groups.all()
        assert all_ygs.count() == 1
        assert yg in all_ygs

    def test_create_new_fails_when_timetable_slot_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Timetable slots with the same id / school, due to unique_together on the
        Meta class.
        """
        # Make a slot to block uniqueness
        slot = factories.TimetableSlot()

        # Try making a slot with the same ID
        with pytest.raises(IntegrityError):
            models.TimetableSlot.create_new(
                school_id=slot.school.school_access_key,
                slot_id=slot.slot_id,
                day_of_week=constants.Day.TUESDAY,
                period_starts_at=dt.time(hour=10),
                period_ends_at=dt.time(hour=11),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_fails_with_invalid_day_of_week(self):
        """
        Tests that we can cannot create two Timetable slots with the same id / school, due to unique_together on the
        Meta class.
        """
        # Make a school for the timetable slot
        school = factories.School()

        # Try making a slot with invalid day of week
        with pytest.raises(ValueError):
            models.TimetableSlot.create_new(
                school_id=school.school_access_key,
                slot_id=1,
                day_of_week=100,
                period_starts_at=dt.time(hour=9),
                period_ends_at=dt.time(hour=10),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_fails_with_equal_start_and_end(self):
        """
        Tests that we can cannot create a Timetable slot with 0s duration.
        """
        # Make a school for the timetable slot
        school = factories.School()

        # Try making a slot with invalid day of week
        with pytest.raises(exceptions.ValidationError):
            models.TimetableSlot.create_new(
                school_id=school.school_access_key,
                slot_id=1,
                day_of_week=constants.Day.MONDAY,
                period_starts_at=dt.time(hour=9),
                period_ends_at=dt.time(hour=9),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_fails_with_end_time_before_start_time(self):
        """
        Tests that we can cannot create a Timetable slot with end time < start time.
        """
        # Make a school for the timetable slot
        school = factories.School()

        # Try making a slot with invalid day of week
        with pytest.raises(exceptions.ValidationError):
            models.TimetableSlot.create_new(
                school_id=school.school_access_key,
                slot_id=1,
                day_of_week=constants.Day.MONDAY,
                period_starts_at=dt.time(hour=9),
                period_ends_at=dt.time(hour=8),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all timetable slots associated with a school.
        Also, that this does not delete any year groups.
        """
        # Make a slot to delete, and a slot that should persist
        delete_slot = factories.TimetableSlot()
        persist_slot = factories.TimetableSlot()
        assert delete_slot.school != persist_slot

        # Execute test unit
        outcome = models.TimetableSlot.delete_all_instances_for_school(
            school_id=delete_slot.school.school_access_key
        )

        # Check delete_slot was deleted from db, only
        deleted_ref = outcome[1]
        assert deleted_ref["data.TimetableSlot"] == 1

        all_slots = models.TimetableSlot.objects.all()
        assert all_slots.count() == 1
        assert all_slots.first() == persist_slot

    # --------------------
    # Queries tests
    # --------------------

    def test_get_timeslot_ids_on_given_day(self):
        """Test that filtering timeslots by school and day to get the slot ids is working as expected"""
        # Make a year group with a slot on monday
        school = factories.School()
        yg = factories.YearGroup(school=school)
        slot = factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            day_of_week=constants.Day.MONDAY,
        )

        # Make some dummy slots that we don't expect in the outcome
        factories.TimetableSlot()  # Dummy slot at different school
        factories.TimetableSlot(
            school=school,
            day_of_week=constants.Day.TUESDAY,  # Dummy slot on different day
        )
        factories.TimetableSlot(  # Dummy slot not for this year group
            school=school,
            day_of_week=constants.Day.MONDAY,
        )

        # Execute test unit
        slots = models.TimetableSlot.get_timeslot_ids_on_given_day(
            school_id=school.school_access_key,
            day_of_week=constants.Day.MONDAY,
            year_group=yg,
        )

        # Check outcome
        assert set(slots) == {slot.slot_id}

    def test_get_unique_start_hours(self):
        """
        Test that the correct set of timeslots, and the correct ordering, is returned by get_unique_start_times
        """
        # Make some slots with different start times
        school = factories.School()
        factories.TimetableSlot(period_starts_at=dt.time(hour=9), school=school)
        factories.TimetableSlot(period_starts_at=dt.time(hour=10), school=school)
        factories.TimetableSlot(period_starts_at=dt.time(hour=14), school=school)
        factories.TimetableSlot(
            period_starts_at=dt.time(hour=9, minute=15), school=school
        )

        # Execute test unit
        timeslots = models.TimetableSlot.get_unique_start_hours(
            school_id=school.school_access_key
        )

        # Check outcome
        assert timeslots == [dt.time(hour=9), dt.time(hour=10), dt.time(hour=14)]

    def test_if_slots_are_consecutive_true(self):
        """
        Tests that consecutive time slots are correctly identified.
        """
        # Get two consecutive slots
        slot_1 = factories.TimetableSlot()
        slot_2 = factories.TimetableSlot.get_next_consecutive_slot(slot_1)

        # Execute test unit
        consecutive_1 = slot_1.check_if_slots_are_consecutive(slot_2)
        consecutive_2 = slot_2.check_if_slots_are_consecutive(slot_1)

        # Check outcome
        assert consecutive_1 and consecutive_2

    def test_if_slots_are_consecutive_false_different_days(self):
        """
        Tests that slots on different days are not called consecutive
        """
        # Get two slots at the same time but on different days
        slot_1 = factories.TimetableSlot(
            period_starts_at=dt.time(hour=9),
            period_ends_at=dt.time(hour=10),
            day_of_week=constants.Day.MONDAY,
        )
        slot_2 = factories.TimetableSlot(
            period_starts_at=dt.time(hour=10),
            period_ends_at=dt.time(hour=11),
            day_of_week=constants.Day.TUESDAY,
        )

        # Execute test unit
        consecutive_1 = slot_1.check_if_slots_are_consecutive(slot_2)
        consecutive_2 = slot_2.check_if_slots_are_consecutive(slot_1)

        # Check outcome
        assert (not consecutive_1) and (not consecutive_2)

    def test_if_slots_are_consecutive_not_contiguous_times_gives_false(self):
        """
        Tests that slots not starting / ending at the same time are not called consecutive
        """
        # Get two slots at the same time but on different days
        slot_1 = factories.TimetableSlot(
            period_starts_at=dt.time(hour=9),
            period_ends_at=dt.time(hour=10),
            day_of_week=constants.Day.MONDAY,
        )
        slot_2 = factories.TimetableSlot(
            period_starts_at=dt.time(hour=10, minute=1),
            period_ends_at=dt.time(hour=11),
            day_of_week=constants.Day.MONDAY,
        )

        # Execute test unit
        consecutive_1 = slot_1.check_if_slots_are_consecutive(slot_2)
        consecutive_2 = slot_2.check_if_slots_are_consecutive(slot_1)

        # Check outcome
        assert (not consecutive_1) and (not consecutive_2)

    # --------------------
    # Properties tests
    # --------------------

    def test_open_interval(self):
        """
        Test the correct open start / finish time is returned for a timetable slot.
        """
        # Get the test slot
        slot = factories.TimetableSlot(
            period_starts_at=dt.time(hour=9), period_ends_at=dt.time(hour=10)
        )

        # Get the open interval
        open_start, open_end = slot.open_interval

        # Check a second is incremented either way
        assert open_start == dt.time(hour=9, minute=0, second=1)
        assert open_end == dt.time(hour=9, minute=59, second=59)
