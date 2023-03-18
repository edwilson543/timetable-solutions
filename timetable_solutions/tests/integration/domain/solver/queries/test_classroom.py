"""
Tests for solver-related queries of the classroom model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants
from domain.solver.queries import classroom as classroom_solver_queries
from tests import data_factories


@pytest.mark.django_db
class TestCheckIfClassroomBusyAtTime:
    def test_busy_when_classroom_has_lesson_at_checked_time(
        self,
    ):
        # Make a classroom who with a lesson fixed at some slot
        classroom = data_factories.Classroom()
        slot = data_factories.TimetableSlot(school=classroom.school)
        data_factories.Lesson(
            school=classroom.school,
            classroom=classroom,
            user_defined_time_slots=(slot,),
        )

        # Check if busy
        clashing_slots = classroom_solver_queries.check_if_classroom_occupied_at_time(
            classroom=classroom,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        # Check classroom successfully made busy
        assert clashing_slots.get() == slot

    def test_busy_when_has_timeslot_partially_overlapping_time(self):
        """
        Test that a classroom is busy if it is occupied at another slot with
        slightly overlapping slots
        """
        # Make a classroom with a lesson fixed at some slot
        classroom = data_factories.Classroom()
        busy_slot = data_factories.TimetableSlot(
            school=classroom.school,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )
        data_factories.Lesson(
            school=classroom.school,
            classroom=classroom,
            user_defined_time_slots=(busy_slot,),
        )

        # Check if busy
        clashing_slots = classroom_solver_queries.check_if_classroom_occupied_at_time(
            classroom=classroom,
            starts_at=dt.time(hour=9, minute=30),
            ends_at=dt.time(hour=10, minute=30),
            day_of_week=busy_slot.day_of_week,
        )

        # Check classroom successfully made busy
        assert clashing_slots.get() == busy_slot

    def test_not_busy_when_classroom_not_in_use(self):
        classroom = data_factories.Classroom()

        # Check if busy
        clash = classroom_solver_queries.check_if_classroom_occupied_at_time(
            classroom=classroom,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=constants.Day.MONDAY,
        )

        # Check classroom successfully made busy
        assert not clash
