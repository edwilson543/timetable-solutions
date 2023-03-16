"""
Tests for data management timetable slot queries.
"""

# Third party imports
import pytest

# Local application imports
from data import constants
from domain.data_management.timetable_slot import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetTimetableSlots:
    def test_gets_timetable_slot_matching_id(self):
        slot = data_factories.TimetableSlot(slot_id=1)

        # This slot will not match the slot_id
        data_factories.TimetableSlot(school=slot.school, slot_id=2)
        # This slot will be for a different school
        data_factories.TimetableSlot(slot_id=1)

        slots = queries.get_timetable_slots(
            school_id=slot.school.school_access_key, slot_id=slot.slot_id
        )

        assert slots.get() == slot

    def test_gets_timetable_slot_matching_day(self):
        slot = data_factories.TimetableSlot(day_of_week=constants.Day.MONDAY)

        # This slot will not match the day of the week
        data_factories.TimetableSlot(
            school=slot.school, day_of_week=constants.Day.TUESDAY
        )
        # This slot will be for a different school
        data_factories.TimetableSlot(day_of_week=constants.Day.MONDAY)

        slots = queries.get_timetable_slots(
            school_id=slot.school.school_access_key, day=slot.day_of_week
        )

        assert slots.get() == slot

    def test_gets_timetable_slot_matching_year_group(self):
        yg = data_factories.YearGroup()
        slot = data_factories.TimetableSlot(
            school=yg.school, relevant_year_groups=(yg,)
        )

        # This slot will not be associated with the relevant year group
        data_factories.TimetableSlot(school=slot.school)

        slots = queries.get_timetable_slots(
            school_id=slot.school.school_access_key, year_group=yg
        )

        assert slots.get() == slot

    def test_gets_timetable_slot_matching_multiple_parameters(self):
        slot = data_factories.TimetableSlot()

        # The second slot will be for a different school
        data_factories.TimetableSlot(slot_id=slot.slot_id, day_of_week=slot.day_of_week)

        slots = queries.get_timetable_slots(
            school_id=slot.school.school_access_key,
            slot_id=slot.slot_id,
            day=slot.day_of_week,
        )

        assert slots.get() == slot


@pytest.mark.django_db
class TestGetNextIdForSchool:
    def test_gets_next_slot_id_when_school_has_slots(self):
        school = data_factories.School()
        slot_a = data_factories.TimetableSlot(school=school)
        slot_b = data_factories.TimetableSlot(school=school)

        next_id = queries.get_next_slot_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == max(slot_a.slot_id, slot_b.slot_id) + 1

    def test_gets_one_when_school_has_no_slots(self):
        school = data_factories.School()

        next_id = queries.get_next_slot_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == 1
