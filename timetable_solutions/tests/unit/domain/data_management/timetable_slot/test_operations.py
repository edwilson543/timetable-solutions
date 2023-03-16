"""Unit tests for timetable slot operations"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants, models
from domain.data_management.timetable_slot import operations
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

        with pytest.raises(operations.UnableToCreateTimetableSlot) as exc:
            operations.create_new_timetable_slot(
                school_id=slot.school.school_access_key,
                slot_id=slot.slot_id,
                day_of_week=constants.Day.MONDAY,
                starts_at=dt.time(hour=9),
                ends_at=dt.time(hour=10),
                relevant_year_groups=models.YearGroup.objects.all(),
            )

        assert (
            "Could not create timetable slot with the given data."
            in exc.value.human_error_message
        )


@pytest.mark.django_db
class TestUpdateTimetableSlotTimings:
    def test_can_update_slot_to_valid_time(self):
        slot = data_factories.TimetableSlot()

        updated_slot = operations.update_timetable_slot_timings(
            slot=slot,
            day_of_week=constants.Day.FRIDAY,
            starts_at=dt.time(hour=15),
            ends_at=dt.time(hour=16),
        )

        assert updated_slot.day_of_week == constants.Day.FRIDAY
        assert updated_slot.starts_at == dt.time(hour=15)
        assert updated_slot.ends_at == dt.time(hour=16)

    def test_raises_if_updating_slot_to_invalid_time(self):
        slot = data_factories.TimetableSlot()

        with pytest.raises(operations.UnableToUpdateTimetableSlotTimings):
            operations.update_timetable_slot_timings(
                slot=slot,
                day_of_week=constants.Day.FRIDAY,
                starts_at=dt.time(hour=16),
                ends_at=dt.time(hour=15),
            )


@pytest.mark.django_db
class TestUpdateTimetableSlotYearGroups:
    def test_can_update_relevant_year_groups(self):
        slot = data_factories.TimetableSlot()

        yg_a = data_factories.YearGroup(school=slot.school)
        yg_b = data_factories.YearGroup(school=slot.school)
        ygs = models.YearGroup.objects.all()

        updated_slot = operations.update_timetable_slot_year_groups(
            slot=slot, relevant_year_groups=ygs
        )

        assert updated_slot.relevant_year_groups.count() == 2
        assert yg_a in updated_slot.relevant_year_groups.all()
        assert yg_b in updated_slot.relevant_year_groups.all()


@pytest.mark.django_db
class TestDeleteTimetableSlot:
    def test_can_delete_timetable_slot(self):
        slot = data_factories.TimetableSlot()

        operations.delete_timetable_slot(slot)

        with pytest.raises(models.TimetableSlot.DoesNotExist):
            slot.refresh_from_db()
