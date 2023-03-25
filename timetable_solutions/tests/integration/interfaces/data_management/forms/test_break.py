"""
Integration tests for forms relating to the Break model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants
from interfaces.data_management.forms import break_ as break_forms
from tests import data_factories


@pytest.mark.django_db
class TestBreakUpdateYearGroups:
    def test_updated_break_with_no_clashes_valid(self):
        yg = data_factories.YearGroup()
        other_yg = data_factories.YearGroup(school=yg.school)
        break_ = data_factories.Break(relevant_year_groups=(yg,), school=yg.school)

        form = break_forms.BreakUpdateYearGroups(
            school_id=break_.school.school_access_key,
            break_=break_,
            data={
                "relevant_year_groups": [yg.pk, other_yg.pk],
            },
        )

        pre_checked = form.base_fields["relevant_year_groups"].initial
        assert list(pre_checked) == [yg.pk]
        assert form.is_valid()

        assert form.cleaned_data["relevant_year_groups"].count() == 2

    def test_break_invalid_if_no_year_group_selected(self):
        yg = data_factories.YearGroup()
        break_ = data_factories.Break(school=yg.school)

        form = break_forms.BreakUpdateYearGroups(
            school_id=break_.school.school_access_key,
            break_=break_,
            data={
                "relevant_year_groups": [],
            },
        )

        assert not form.is_valid()
        assert "You must select at least one year group!" in form.errors.as_text()

    def test_updated_break_with_break_clash_invalid(self):
        school = data_factories.School()
        break_ = data_factories.Break(school=school)

        # We'll try assigning the first break to a year group
        # that already has a break at the same time
        yg = data_factories.YearGroup(school=school)
        other_break = data_factories.Break(
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
            relevant_year_groups=(yg,),
            school=school,
        )

        form = break_forms.BreakUpdateYearGroups(
            school_id=break_.school.school_access_key,
            break_=break_,
            data={
                "relevant_year_groups": [yg.pk],
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{other_break.starts_at.strftime("%H:%M")}-{other_break.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "break" in error_message

    def test_updated_break_with_year_group_slot_clash_invalid(self):
        school = data_factories.School()
        break_ = data_factories.Break(school=school)

        # We'll try assigning the first slot to a year group
        # that already has a slot at the same time
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
            relevant_year_groups=(yg,),
            school=school,
        )

        form = break_forms.BreakUpdateYearGroups(
            school_id=break_.school.school_access_key,
            break_=break_,
            data={
                "relevant_year_groups": [yg.pk],
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{slot.starts_at.strftime("%H:%M")}-{slot.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "slot" in error_message

    def test_updated_break_with_break_and_slot_clash_invalid(self):
        school = data_factories.School()
        break_ = data_factories.Break(school=school)

        # We'll try assigning the first slot to a year group
        # that already has a break at the same time
        yg = data_factories.YearGroup(school=school)
        data_factories.Break(
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
            relevant_year_groups=(yg,),
            school=school,
        )

        # ... and another year group that already has a slot at this time
        other_yg = data_factories.YearGroup(school=school)
        data_factories.TimetableSlot(
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
            relevant_year_groups=(other_yg,),
            school=school,
        )

        form = break_forms.BreakUpdateYearGroups(
            school_id=break_.school.school_access_key,
            break_=break_,
            data={
                "relevant_year_groups": [yg.pk, other_yg.pk],
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert "slot" in error_message
        assert "break" in error_message


@pytest.mark.django_db
class TestBreakUpdateTimings:
    def test_updated_break_with_no_clashes_valid(self):
        break_ = data_factories.Break()

        form = break_forms.BreakUpdateTimings(
            school_id=break_.school.school_access_key,
            break_=break_,
            data={
                "break_name": "my-break",
                "starts_at": dt.time(hour=8),
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
            },
        )

        assert form.is_valid()

    def test_updating_break_to_same_time_valid(self):
        break_ = data_factories.Break()

        form = break_forms.BreakUpdateTimings(
            school_id=break_.school.school_access_key,
            break_=break_,
            data={
                "break_name": "my-break",
                "starts_at": break_.starts_at,
                "ends_at": break_.ends_at,
                "day_of_week": break_.day_of_week,
            },
        )

        assert form.is_valid()

    def test_updated_break_with_year_group_break_clash_invalid(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        break_ = data_factories.Break(relevant_year_groups=(yg,), school=school)

        # Create a break at the attempted update time
        other_break = data_factories.Break(relevant_year_groups=(yg,), school=school)

        form = break_forms.BreakUpdateTimings(
            school_id=school.school_access_key,
            break_=break_,
            data={
                "starts_at": other_break.starts_at,
                "ends_at": other_break.ends_at,
                "day_of_week": other_break.day_of_week,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{other_break.starts_at.strftime("%H:%M")}-{other_break.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "break" in error_message

    def test_updated_break_with_teacher_break_clash_invalid(self):
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        break_ = data_factories.Break(teachers=(teacher,), school=school)

        # Create a break at the attempted update time
        other_break = data_factories.Break(teachers=(teacher,), school=school)

        form = break_forms.BreakUpdateTimings(
            school_id=school.school_access_key,
            break_=break_,
            data={
                "starts_at": other_break.starts_at,
                "ends_at": other_break.ends_at,
                "day_of_week": other_break.day_of_week,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{other_break.starts_at.strftime("%H:%M")}-{other_break.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "break" in error_message

    def test_updated_break_with_year_group_slot_clash_invalid(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        break_ = data_factories.Break(relevant_year_groups=(yg,), school=school)

        # Create a slot at the attempted update time
        slot = data_factories.TimetableSlot(relevant_year_groups=(yg,), school=school)

        form = break_forms.BreakUpdateTimings(
            school_id=school.school_access_key,
            break_=break_,
            data={
                "starts_at": slot.starts_at,
                "ends_at": slot.ends_at,
                "day_of_week": slot.day_of_week,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{slot.starts_at.strftime("%H:%M")}-{slot.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "slot" in error_message

    def test_updated_break_with_break_and_slot_year_group_clash_invalid(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        other_yg = data_factories.YearGroup(school=school)
        break_ = data_factories.Break(
            relevant_year_groups=(yg, other_yg), school=school
        )

        # Create a slot at the time we'll try updating to
        slot = data_factories.TimetableSlot(
            school=school, relevant_year_groups=(other_yg,)
        )
        data_factories.Break(
            relevant_year_groups=(other_yg,),
            school=school,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        form = break_forms.BreakUpdateTimings(
            school_id=school.school_access_key,
            break_=break_,
            data={
                "starts_at": slot.starts_at,
                "ends_at": slot.ends_at,
                "day_of_week": slot.day_of_week,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert "slot" in error_message
        assert "break" in error_message


@pytest.mark.django_db
class TestBreakCreate:
    @pytest.mark.parametrize("relevant_to_all_year_groups", [True, False])
    @pytest.mark.parametrize("relevant_to_all_teachers", [True, False])
    def test_new_break_with_no_clashes_valid(
        self, relevant_to_all_year_groups: bool, relevant_to_all_teachers: bool
    ):
        school = data_factories.School()
        data_factories.YearGroup(school=school)
        data_factories.Teacher(school=school)

        form = break_forms.BreakCreate(
            school_id=school.school_access_key,
            data={
                "break_id": "my-break",
                "break_name": "Monday morning",
                "starts_at": dt.time(hour=8),
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
                "relevant_to_all_year_groups": relevant_to_all_year_groups,
                "relevant_to_all_teacher": relevant_to_all_teachers,
            },
        )

        assert form.is_valid()

    def test_new_break_missing_fields_invalid(self):
        school = data_factories.School()
        data_factories.YearGroup(school=school)
        data_factories.Teacher(school=school)

        form = break_forms.BreakCreate(
            school_id=school.school_access_key,
            data={
                "starts_at": dt.time(hour=8),
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
            },
        )

        assert not form.is_valid()
        assert "This field is required" in form.errors.as_text()

    def test_new_break_with_year_group_break_clash_invalid(self):
        break_ = data_factories.Break()

        form = break_forms.BreakCreate(
            school_id=break_.school.school_access_key,
            data={
                "break_id": "my-break",
                "break_name": "Monday morning",
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

    def test_new_break_with_teacher_break_clash_invalid(self):
        school = data_factories.School()
        # Create a teacher with a break clashing with this one
        teacher = data_factories.Teacher(school=school)
        break_ = data_factories.Break(school=school, teachers=(teacher,))

        form = break_forms.BreakCreate(
            school_id=break_.school.school_access_key,
            data={
                "break_id": "my-break",
                "break_name": "Monday morning",
                "starts_at": break_.starts_at,
                "ends_at": break_.ends_at,
                "day_of_week": break_.day_of_week,
                "relevant_to_all_teachers": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert (
            f'{break_.starts_at.strftime("%H:%M")}-{break_.ends_at.strftime("%H:%M")}'
            in error_message
        )
        assert "break" in error_message

    def test_new_break_with_year_group_slot_clash_invalid(self):
        slot = data_factories.TimetableSlot()

        # Submit data for a new slot, which is forced to clash with the fake clashes
        form = break_forms.BreakCreate(
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

    def test_new_break_for_all_year_groups_with_break_and_slot_clash_invalid(self):
        school = data_factories.School()
        break_ = data_factories.Break(school=school)
        data_factories.TimetableSlot(
            school=school,
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
        )

        # Submit data for a new slot, which is forced to clash with the fake clashes
        form = break_forms.BreakCreate(
            school_id=school.school_access_key,
            data={
                "starts_at": break_.starts_at,
                "ends_at": break_.ends_at,
                "day_of_week": break_.day_of_week,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert "slot" in error_message
        assert "break" in error_message
