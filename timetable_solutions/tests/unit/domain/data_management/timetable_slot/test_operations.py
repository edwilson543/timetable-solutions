"""Unit tests for timetable slot operations"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants, models
from domain.data_management.timetable_slot import exceptions, operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewTimetableSlot:
    def test_create_new_valid_slot(self):
        # Make a school and year group for the slot to be associated with
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        # Create a new slot for the school
        operations.create_new_timetable_slot(
            school_id=school.school_access_key,
            slot_id=1,
            day_of_week=constants.Day.MONDAY,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            relevant_year_groups=models.YearGroup.objects.all(),
        )

        # Check slot was created
        slot = models.TimetableSlot.objects.get()

        assert slot.school == school
        assert slot.slot_id == 1
        assert slot.day_of_week == constants.Day.MONDAY
        assert slot.starts_at == dt.time(hour=9)
        assert slot.ends_at == dt.time(hour=10)
        assert slot.relevant_year_groups.get() == yg

    def test_raises_when_slot_id_not_unique_for_school(self):
        slot = data_factories.TimetableSlot()

        with pytest.raises(exceptions.CouldNotCreateTimetableSlot):
            operations.create_new_timetable_slot(
                school_id=slot.school.school_access_key,
                slot_id=1,
                day_of_week=constants.Day.MONDAY,
                starts_at=dt.time(hour=9),
                ends_at=dt.time(hour=10),
                relevant_year_groups=models.YearGroup.objects.all(),
            )
