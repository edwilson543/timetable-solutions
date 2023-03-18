"""
Solver-related queries of the pupil model.
"""
# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants
from domain.solver.queries import pupil as pupil_solver_queries
from tests import data_factories


@pytest.mark.django_db
class TestCheckIfBusyAtTime:
    def test_busy_when_pupil_pupil_has_lesson_at_checked_time(self):
        # Make a pupil and ensure they are busy for some slot
        pupil = data_factories.Pupil()
        slot = data_factories.TimetableSlot(
            school=pupil.school, relevant_year_groups=(pupil.year_group,)
        )
        data_factories.Lesson(
            school=pupil.school, pupils=(pupil,), user_defined_time_slots=(slot,)
        )

        # Check if they are busy
        clash = pupil_solver_queries.check_if_pupil_busy_at_time(
            pupil=pupil,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        # Ensure expected slot in the clashes
        assert clash.slots.get() == slot

    def test_busy_when_pupil_has_break_at_checked_time(self):
        # Make a pupil and ensure they are busy for some slot
        pupil = data_factories.Pupil()
        break_ = data_factories.Break(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )

        # Check if they are busy
        clash = pupil_solver_queries.check_if_pupil_busy_at_time(
            pupil=pupil,
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
        )

        # Ensure expected break in the clashes
        assert clash.breaks.get() == break_

    def test_busy_when_pupil_pupil_has_lesson_at_partially_overlapping_time(self):
        # Make a pupil and ensure they are busy for some slot
        pupil = data_factories.Pupil()
        slot = data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )
        data_factories.Lesson(
            school=pupil.school, pupils=(pupil,), user_defined_time_slots=(slot,)
        )

        # Check if they are busy
        clash = pupil_solver_queries.check_if_pupil_busy_at_time(
            pupil=pupil,
            starts_at=dt.time(hour=9, minute=45),
            ends_at=dt.time(hour=10, minute=15),
            day_of_week=slot.day_of_week,
        )

        # Ensure expected slot in the clashes
        assert clash.slots.get() == slot

    def test_busy_when_pupil_pupil_has_break_at_partially_overlapping_time(self):
        # Make a pupil and ensure they are busy for some slot
        pupil = data_factories.Pupil()
        break_ = data_factories.Break(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )

        # Check if they are busy
        clash = pupil_solver_queries.check_if_pupil_busy_at_time(
            pupil=pupil,
            starts_at=dt.time(hour=9, minute=45),
            ends_at=dt.time(hour=10, minute=15),
            day_of_week=break_.day_of_week,
        )

        # Ensure expected slot in the clashes
        assert clash.breaks.get() == break_

    def test_check_if_busy_at_time_slot_when_pupil_is_not_busy(self):
        # Make a pupil and slot
        pupil = data_factories.Pupil()

        # Check if they are busy
        clash = pupil_solver_queries.check_if_pupil_busy_at_time(
            pupil=pupil,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=constants.Day.MONDAY,
        )

        # Ensure expected break in the clashes
        assert not clash
