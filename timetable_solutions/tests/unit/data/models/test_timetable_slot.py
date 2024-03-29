"""
Unit tests for methods on the TimetableSlot and TimetableSlotQuerySet classes.
"""


# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Local application imports
from data import constants, models
from tests import data_factories as data_factories


@pytest.mark.django_db
class TestTimetableSlotQuerySet:
    """Unit tests for the TimetableSlot QuerySet"""

    def test_get_timeslots_on_given_day_year_one(self):
        """
        Test that filtering timeslots by school and day is working as expected.
        In particular that only the year groups relevant to year 1 are returned.
        """
        # Make a year group with a slot on monday
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            day_of_week=constants.Day.MONDAY,
        )

        # Make some dummy slots that we don't expect in the outcome
        data_factories.TimetableSlot()  # Dummy slot at different school
        data_factories.TimetableSlot(
            school=school,
            day_of_week=constants.Day.TUESDAY,  # Dummy slot on different day
        )
        data_factories.TimetableSlot(  # Dummy slot not for this year group
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


@pytest.mark.django_db
class TestCreateNewTimetableSlot:
    def test_create_new_valid_timeslot(self):
        # Make a school and year group for the timetable slot
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        # Make a slot at the school
        slot = models.TimetableSlot.create_new(
            school_id=school.school_access_key,
            slot_id=1,
            day_of_week=constants.Day.MONDAY,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            relevant_year_groups=models.YearGroup.objects.all(),
        )

        # Check slot saved to db and defined as expected
        all_slots = models.TimetableSlot.objects.all()
        assert all_slots.get() == slot

        all_ygs = slot.relevant_year_groups.all()
        assert all_ygs.get() == yg

    def test_create_new_fails_when_timetable_slot_id_not_unique_for_school(self):
        # Make a slot to block uniqueness
        slot = data_factories.TimetableSlot()

        # Try making a slot with the same ID
        with pytest.raises(IntegrityError):
            models.TimetableSlot.create_new(
                school_id=slot.school.school_access_key,
                slot_id=slot.slot_id,
                day_of_week=constants.Day.TUESDAY,
                starts_at=dt.time(hour=10),
                ends_at=dt.time(hour=11),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_fails_with_invalid_day_of_week(self):
        # Make a school for the timetable slot
        school = data_factories.School()

        # Try making a slot with invalid day of week
        with pytest.raises(ValidationError):
            models.TimetableSlot.create_new(
                school_id=school.school_access_key,
                slot_id=1,
                day_of_week=100,
                starts_at=dt.time(hour=9),
                ends_at=dt.time(hour=10),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_fails_with_equal_start_and_end_time(self):
        school = data_factories.School()

        with pytest.raises(IntegrityError):
            models.TimetableSlot.create_new(
                school_id=school.school_access_key,
                slot_id=1,
                day_of_week=constants.Day.MONDAY,
                starts_at=dt.time(hour=9),
                ends_at=dt.time(hour=9),  # Note these are the same
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_fails_with_end_time_before_start_time(self):
        """
        Tests that we can cannot create a Timetable slot with end time < start time.
        """
        # Make a school for the timetable slot
        school = data_factories.School()

        # Try making a slot with invalid day of week
        with pytest.raises(IntegrityError):
            models.TimetableSlot.create_new(
                school_id=school.school_access_key,
                slot_id=1,
                day_of_week=constants.Day.MONDAY,
                starts_at=dt.time(hour=9),
                ends_at=dt.time(hour=8),
                relevant_year_groups=models.YearGroup.objects.none(),
            )


@pytest.mark.django_db
class TestUpdateSlotTimings:
    def test_can_update_slot_to_valid_time(self):
        slot = data_factories.TimetableSlot()

        slot.update_slot_timings(
            day_of_week=constants.Day.FRIDAY,
            starts_at=dt.time(hour=15),
            ends_at=dt.time(hour=16),
        )

        slot.refresh_from_db()
        assert slot.day_of_week == constants.Day.FRIDAY
        assert slot.starts_at == dt.time(hour=15)
        assert slot.ends_at == dt.time(hour=16)

    def test_raises_if_updating_slot_to_invalid_time(self):
        slot = data_factories.TimetableSlot()

        with pytest.raises(IntegrityError):
            slot.update_slot_timings(
                day_of_week=constants.Day.FRIDAY,
                starts_at=dt.time(hour=16),
                ends_at=dt.time(hour=16),
            )


@pytest.mark.django_db
class TestUpdateRelevantYearGroups:
    def test_can_update_relevant_year_groups(self):
        slot = data_factories.TimetableSlot()

        yg_a = data_factories.YearGroup(school=slot.school)
        yg_b = data_factories.YearGroup(school=slot.school)
        ygs = models.YearGroup.objects.all()

        slot.update_relevant_year_groups(relevant_year_groups=ygs)

        slot.refresh_from_db()
        assert slot.relevant_year_groups.count() == 2
        assert yg_a in slot.relevant_year_groups.all()
        assert yg_b in slot.relevant_year_groups.all()


@pytest.mark.django_db
class TestDeleteAllInstancesForSchool:
    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all timetable slots associated with a school.
        Also, that this does not delete any year groups.
        """
        # Make a slot to delete, and a slot that should persist
        delete_slot = data_factories.TimetableSlot()
        persist_slot = data_factories.TimetableSlot()
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
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            day_of_week=constants.Day.MONDAY,
        )

        # Make some dummy slots that we don't expect in the outcome
        data_factories.TimetableSlot()  # Dummy slot at different school
        data_factories.TimetableSlot(
            school=school,
            day_of_week=constants.Day.TUESDAY,  # Dummy slot on different day
        )
        data_factories.TimetableSlot(  # Dummy slot not for this year group
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
        school = data_factories.School()
        data_factories.TimetableSlot(starts_at=dt.time(hour=9), school=school)
        data_factories.TimetableSlot(starts_at=dt.time(hour=10), school=school)
        data_factories.TimetableSlot(starts_at=dt.time(hour=14), school=school)
        data_factories.TimetableSlot(
            starts_at=dt.time(hour=9, minute=15), school=school
        )

        # Execute test unit
        timeslots = models.TimetableSlot.get_unique_start_hours(
            school_id=school.school_access_key
        )

        # Check outcome
        assert timeslots == [dt.time(hour=9), dt.time(hour=10), dt.time(hour=14)]

    def test_get_all_lessons_gives_solver_and_user_lessons(self):
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)
        user_lesson = data_factories.Lesson(
            school=school, user_defined_time_slots=(slot,)
        )
        solver_lesson = data_factories.Lesson(
            school=school, solver_defined_time_slots=(slot,)
        )
        # Make some random other lesson
        data_factories.Lesson(school=school)

        lessons = slot.get_all_lessons()

        assert lessons.count() == 2
        assert user_lesson in lessons
        assert solver_lesson in lessons

    def test_if_slots_are_consecutive_true(self):
        """
        Tests that consecutive time slots are correctly identified.
        """
        # Get two consecutive slots
        slot_1 = data_factories.TimetableSlot()
        slot_2 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_1)

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
        slot_1 = data_factories.TimetableSlot(
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=constants.Day.MONDAY,
        )
        slot_2 = data_factories.TimetableSlot(
            starts_at=dt.time(hour=10),
            ends_at=dt.time(hour=11),
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
        slot_1 = data_factories.TimetableSlot(
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=constants.Day.MONDAY,
        )
        slot_2 = data_factories.TimetableSlot(
            starts_at=dt.time(hour=10, minute=1),
            ends_at=dt.time(hour=11),
            day_of_week=constants.Day.MONDAY,
        )

        # Execute test unit
        consecutive_1 = slot_1.check_if_slots_are_consecutive(slot_2)
        consecutive_2 = slot_2.check_if_slots_are_consecutive(slot_1)

        # Check outcome
        assert (not consecutive_1) and (not consecutive_2)
