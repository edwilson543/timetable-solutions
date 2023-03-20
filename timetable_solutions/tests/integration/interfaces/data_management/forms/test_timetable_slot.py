"""
Integration tests for forms relating to the TimetableSlot model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants
from interfaces.data_management.forms import timetable_slot as timetable_slot_forms
from tests import data_factories


@pytest.mark.django_db
class TestTimetableSlotUpdateTimings:
    @pytest.mark.parametrize("relevant_to_all_year_groups", [True, False])
    def test_updated_slot_with_no_clashes_valid(
        self, relevant_to_all_year_groups: bool
    ):
        # Some validation only runs for slots with year groups, so make one
        yg = data_factories.YearGroup()
        slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg,), school=yg.school
        )

        form = timetable_slot_forms.TimetableSlotUpdateTimings(
            school_id=slot.school.school_access_key,
            slot=slot,
            data={
                "starts_at": dt.time(hour=8),
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
                "relevant_to_all_year_groups": relevant_to_all_year_groups,
            },
        )

        assert form.is_valid()

    def test_updating_slot_to_same_time_valid(self):
        # Some validation only runs for slots with year grups, so make one
        yg = data_factories.YearGroup()
        slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg,), school=yg.school
        )

        form = timetable_slot_forms.TimetableSlotUpdateTimings(
            school_id=slot.school.school_access_key,
            slot=slot,
            data={
                "starts_at": slot.starts_at,
                "ends_at": slot.ends_at,
                "day_of_week": slot.day_of_week,
                "relevant_to_all_year_groups": False,
            },
        )

        assert form.is_valid()

    def test_updated_slot_with_year_group_clash_invalid(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(relevant_year_groups=(yg,), school=school)

        # Create a slot at the attempted update time
        other_slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg,), school=school
        )

        form = timetable_slot_forms.TimetableSlotUpdateTimings(
            school_id=school.school_access_key,
            slot=slot,
            data={
                "starts_at": other_slot.starts_at,
                "ends_at": other_slot.ends_at,
                "day_of_week": other_slot.day_of_week,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{slot.starts_at.strftime("%H:%M")}-{slot.ends_at.strftime("%H:%M")}'
            in error_message
        )

    def test_updated_slot_with_break_clash_invalid(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(relevant_year_groups=(yg,), school=school)

        # Create a break at the attempted update time
        break_ = data_factories.Break(relevant_year_groups=(yg,), school=school)

        form = timetable_slot_forms.TimetableSlotUpdateTimings(
            school_id=school.school_access_key,
            slot=slot,
            data={
                "starts_at": break_.starts_at,
                "ends_at": break_.ends_at,
                "day_of_week": break_.day_of_week,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{break_.starts_at.strftime("%H:%M")}-{break_.ends_at.strftime("%H:%M")}'
            in error_message
        )

    def test_updated_slot_with_slot_and_break_clash_invalid(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(relevant_year_groups=(yg,), school=school)

        # Create a slot and a break at the attempted update time
        other_slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg,), school=school
        )
        data_factories.Break(
            relevant_year_groups=(yg,),
            school=school,
            starts_at=other_slot.starts_at,
            ends_at=other_slot.ends_at,
            day_of_week=other_slot.day_of_week,
        )

        form = timetable_slot_forms.TimetableSlotUpdateTimings(
            school_id=school.school_access_key,
            slot=slot,
            data={
                "starts_at": other_slot.starts_at,
                "ends_at": other_slot.ends_at,
                "day_of_week": other_slot.day_of_week,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert "slot" in error_message
        assert "break" in error_message


@pytest.mark.django_db
class TestTimetableSlotCreate:
    @pytest.mark.parametrize("relevant_to_all_year_groups", [True, False])
    def test_new_slot_with_no_clashes_valid(self, relevant_to_all_year_groups: bool):
        school = data_factories.School()

        form = timetable_slot_forms.TimetableSlotCreate(
            school_id=school.school_access_key,
            data={
                "starts_at": dt.time(hour=8),
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
                "relevant_to_all_year_groups": relevant_to_all_year_groups,
            },
        )

        assert form.is_valid()

    def test_new_slot_with_slot_clash_invalid(self):
        # Include a year group so the year group validation logic runs
        slot = data_factories.TimetableSlot()

        # Submit data for a new slot, which is forced to clash with the fake clashes
        form = timetable_slot_forms.TimetableSlotCreate(
            school_id=slot.school.school_access_key,
            data={
                "starts_at": slot.starts_at,
                "ends_at": slot.ends_at,
                "day_of_week": slot.day_of_week,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{slot.starts_at.strftime("%H:%M")}-{slot.ends_at.strftime("%H:%M")}'
            in error_message
        )

    def test_new_slot_with_break_clash_invalid(self):
        break_ = data_factories.Break()

        # Submit data for a new slot, which is forced to clash with the fake clashes
        form = timetable_slot_forms.TimetableSlotCreate(
            school_id=break_.school.school_access_key,
            data={
                "starts_at": break_.starts_at,
                "ends_at": break_.ends_at,
                "day_of_week": break_.day_of_week,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{break_.starts_at.strftime("%H:%M")}-{break_.ends_at.strftime("%H:%M")}'
            in error_message
        )

    def test_new_slot_with_slot_and_break_clash_invalid(self):
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)
        data_factories.Break(
            school=school,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        # Submit data for a new slot, which is forced to clash with the fake clashes
        form = timetable_slot_forms.TimetableSlotCreate(
            school_id=school.school_access_key,
            data={
                "starts_at": slot.starts_at,
                "ends_at": slot.ends_at,
                "day_of_week": slot.day_of_week,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert "slot" in error_message
        assert "break" in error_message
