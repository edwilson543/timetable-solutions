"""
Unit tests for forms relating to the TimetableSlot model.
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
