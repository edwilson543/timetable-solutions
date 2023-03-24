"""
Integration tests for forms relating to the Break model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants, models
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

    def test_updated_slot_with_slot_and_break_clash_invalid(self):
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
