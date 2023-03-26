"""
Integration tests for forms relating to the TimetableSlot model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants, models
from interfaces.data_management.forms import timetable_slot as timetable_slot_forms
from tests import data_factories


@pytest.mark.django_db
class TestTimetableSlotUpdateYearGroups:
    def test_updated_slot_with_no_clashes_valid(self):
        yg = data_factories.YearGroup()
        other_yg = data_factories.YearGroup(school=yg.school)
        slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg,), school=yg.school
        )

        form = timetable_slot_forms.TimetableSlotUpdateYearGroups(
            school_id=slot.school.school_access_key,
            slot=slot,
            data={
                "relevant_year_groups": [yg.pk, other_yg.pk],
            },
        )

        pre_checked = form.fields["relevant_year_groups"].initial
        assert list(pre_checked) == [yg.pk]
        assert form.is_valid()

        all_ygs = models.YearGroup.objects.all()
        assert (
            form.cleaned_data["relevant_year_groups"] & all_ygs
        ).count() == all_ygs.count()

    def test_form_invalid_if_no_year_group_selected(self):
        yg = data_factories.YearGroup()
        slot = data_factories.TimetableSlot(school=yg.school)

        form = timetable_slot_forms.TimetableSlotUpdateYearGroups(
            school_id=slot.school.school_access_key,
            slot=slot,
            data={
                "relevant_year_groups": [],
            },
        )

        assert not form.is_valid()
        assert "You must select at least one year group!" in form.errors.as_text()

    def test_form_invalid_if_slot_in_use_for_lesson_for_removed_year_group(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))

        # Make a lesson using this slot
        pupil = data_factories.Pupil(school=school, year_group=yg)
        data_factories.Lesson(
            school=school, pupils=(pupil,), user_defined_time_slots=(slot,)
        )

        # Create some other yg to select so we don't get the no year groups error
        other_yg = data_factories.YearGroup(school=school)

        form = timetable_slot_forms.TimetableSlotUpdateYearGroups(
            school_id=slot.school.school_access_key,
            slot=slot,
            data={
                "relevant_year_groups": [other_yg.pk],
            },
        )

        assert not form.is_valid()
        assert (
            f"Cannot unassign year group(s) {yg.year_group_name} from this slot"
            in form.errors.as_text()
        )

    def test_updated_slot_with_year_group_clash_invalid(self):
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)

        # We'll try assigning the first slot to a year group
        # that already has a slot at the same time
        yg = data_factories.YearGroup(school=school)
        other_slot = data_factories.TimetableSlot(
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
            relevant_year_groups=(yg,),
            school=school,
        )

        form = timetable_slot_forms.TimetableSlotUpdateYearGroups(
            school_id=slot.school.school_access_key,
            slot=slot,
            data={
                "relevant_year_groups": [yg.pk],
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{other_slot.starts_at.strftime("%H:%M")}-{other_slot.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "slot" in error_message

    def test_updated_slot_with_break_clash_invalid(self):
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)

        # We'll try assigning the first slot to a year group
        # that already has a break at the same time
        yg = data_factories.YearGroup(school=school)
        break_ = data_factories.Break(
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
            relevant_year_groups=(yg,),
            school=school,
        )

        form = timetable_slot_forms.TimetableSlotUpdateYearGroups(
            school_id=slot.school.school_access_key,
            slot=slot,
            data={
                "relevant_year_groups": [yg.pk],
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{break_.starts_at.strftime("%H:%M")}-{break_.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "break" in error_message

    def test_updated_slot_with_slot_and_break_clash_invalid(self):
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)

        # We'll try assigning the first slot to a year group
        # that already has a break at the same time
        yg = data_factories.YearGroup(school=school)
        data_factories.Break(
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
            relevant_year_groups=(yg,),
            school=school,
        )

        # ... and another year group that already has a slot at this time
        other_yg = data_factories.YearGroup(school=school)
        data_factories.TimetableSlot(
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
            relevant_year_groups=(other_yg,),
            school=school,
        )

        form = timetable_slot_forms.TimetableSlotUpdateYearGroups(
            school_id=slot.school.school_access_key,
            slot=slot,
            data={
                "relevant_year_groups": [yg.pk, other_yg.pk],
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert "slot" in error_message
        assert "break" in error_message


@pytest.mark.django_db
class TestTimetableSlotUpdateTimings:
    def test_updated_slot_with_no_clashes_valid(self):
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
            },
        )

        assert form.is_valid()

    def test_updating_slot_to_same_time_valid(self):
        # Some validation only runs for slots with year groups, so make one
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
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{other_slot.starts_at.strftime("%H:%M")}-{other_slot.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "slot" in error_message

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
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{break_.starts_at.strftime("%H:%M")}-{break_.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "break" in error_message

    def test_updated_slot_with_slot_and_break_clash_invalid(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        other_yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg, other_yg), school=school
        )

        # Create a slot at the time we'll try updating to
        other_slot = data_factories.TimetableSlot.get_next_consecutive_slot(slot=slot)
        data_factories.Break(
            relevant_year_groups=(other_yg,),
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
        assert "slot" in error_message

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
        assert "break" in error_message

    def test_new_slot_for_all_year_groups_with_slot_and_break_clash_invalid(self):
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
