"""
Tests for forms relating to the TimetableSlot model.
"""

# Standard library imports
import datetime as dt
from unittest import mock

# Third party imports
import pytest

# Local application imports
from data import constants
from interfaces.data_management.forms import timetable_slot as timetable_slot_forms
from tests import data_factories


@pytest.mark.django_db
class TestTimetableSlotCreateUpdateBase:
    def test_valid_slot_form_valid(self):
        school = data_factories.School()

        form = timetable_slot_forms._TimetableSlotCreateUpdateBase(
            school_id=school.school_access_key,
        )
        form.cleaned_data = {
            "starts_at": dt.time(hour=8),
            "ends_at": dt.time(hour=9),
            "day_of_week": constants.Day.MONDAY,
        }

        assert not form.is_valid()

    @pytest.mark.parametrize("starts_at", [dt.time(hour=9), dt.time(hour=9, minute=5)])
    def test_slot_starting_at_or_after_ending_invalid(self, starts_at: dt.time):
        school = data_factories.School()

        form = timetable_slot_forms._TimetableSlotCreateUpdateBase(
            school_id=school.school_access_key,
            data={
                "starts_at": starts_at,
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
            },
        )

        assert form.is_valid()


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

    @pytest.mark.parametrize("n_clashes", [1, 3])
    @mock.patch.object(
        timetable_slot_forms.clash_filters, "filter_queryset_for_clashes"
    )
    def test_new_slot_with_slot_clash_invalid(
        self, mock_filter_for_clashes: mock.Mock, n_clashes: int
    ):
        school = data_factories.School()
        fake_clashes = [
            data_factories.TimetableSlot(school=school) for _ in range(0, n_clashes)
        ]
        mock_filter_for_clashes.return_value = fake_clashes

        # Submit data for a new slot, which is forced to clash with the fake clashes
        form = timetable_slot_forms.TimetableSlotCreate(
            school_id=school.school_access_key,
            data={
                "starts_at": dt.time(hour=8),
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        for slot in fake_clashes:
            assert f"{slot.starts_at}-{slot.ends_at}" in error_message

    @pytest.mark.parametrize("n_clashes", [1, 3])
    @mock.patch.object(
        timetable_slot_forms.clash_filters, "filter_queryset_for_clashes"
    )
    def test_new_slot_with_break_clash_invalid(
        self, mock_filter_for_clashes: mock.Mock, n_clashes: int
    ):
        school = data_factories.School()
        fake_clashes = [
            data_factories.Break(school=school) for _ in range(0, n_clashes)
        ]
        mock_filter_for_clashes.return_value = fake_clashes

        # Submit data for a new slot, which is forced to clash with the fake clashes
        form = timetable_slot_forms.TimetableSlotCreate(
            school_id=school.school_access_key,
            data={
                "starts_at": dt.time(hour=8),
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        for break_ in fake_clashes:
            assert f"{break_.starts_at}-{break_.ends_at}" in error_message

    @mock.patch.object(
        timetable_slot_forms.clash_filters, "filter_queryset_for_clashes"
    )
    def test_new_slot_with_slot_and_break_clash_invalid(
        self, mock_filter_for_clashes: mock.Mock
    ):
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)
        break_ = data_factories.Break(school=school)
        mock_filter_for_clashes.side_effect = [[slot], [break_]]

        # Submit data for a new slot, which is forced to clash with the fake clashes
        form = timetable_slot_forms.TimetableSlotCreate(
            school_id=school.school_access_key,
            data={
                "starts_at": dt.time(hour=8),
                "ends_at": dt.time(hour=9),
                "day_of_week": constants.Day.MONDAY,
                "relevant_to_all_year_groups": True,
            },
        )

        assert not form.is_valid()

        error_message = form.errors.as_text()
        assert "slot" in error_message
        assert "break" in error_message
