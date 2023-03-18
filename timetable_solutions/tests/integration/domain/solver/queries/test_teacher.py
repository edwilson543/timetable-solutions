"""
Tests for solver-related queries of the teacher model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants
from domain.solver.queries import teacher as teacher_solver_queries
from tests import data_factories


@pytest.mark.django_db
class TestCheckIfTeacherBusyAtTime:
    def test_busy_when_teacher_in_lesson_at_checked_time(
        self,
    ):
        # Make a teacher who teaches a lesson fixed at some slot
        teacher = data_factories.Teacher()
        slot = data_factories.TimetableSlot(school=teacher.school)
        data_factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(slot,)
        )

        # Check if busy
        clash = teacher_solver_queries.check_if_teacher_busy_at_time(
            teacher=teacher,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        # Check teacher successfully made busy
        assert clash.slots.get() == slot

    def test_busy_when_teacher_in_break_at_checked_time(self):
        # Make a teacher with a break at some time
        teacher = data_factories.Teacher()

        break_ = data_factories.Break(
            school=teacher.school,
            teachers=(teacher,),
        )

        # Check if busy
        clash = teacher_solver_queries.check_if_teacher_busy_at_time(
            teacher=teacher,
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
        )

        # Check teacher successfully made busy
        assert clash.breaks.get() == break_

    def test_busy_when_has_lesson_at_partially_overlapping_time(self):
        # Make a teacher who teaches a lesson fixed at some slot
        teacher = data_factories.Teacher()
        busy_slot = data_factories.TimetableSlot(
            school=teacher.school,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )
        data_factories.Lesson(
            school=teacher.school, teacher=teacher, user_defined_time_slots=(busy_slot,)
        )

        # Check if busy
        clash = teacher_solver_queries.check_if_teacher_busy_at_time(
            teacher=teacher,
            starts_at=dt.time(hour=9, minute=30),
            ends_at=dt.time(hour=10, minute=30),
            day_of_week=busy_slot.day_of_week,
        )

        # Check teacher successfully made busy
        assert clash.slots.get() == busy_slot

    def test_busy_when_has_break_at_partially_overlapping_time(self):
        # Make a teacher who teaches a lesson fixed at some slot
        teacher = data_factories.Teacher()
        break_ = data_factories.Break(
            school=teacher.school,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            teachers=(teacher,),
        )

        # Check if busy
        clash = teacher_solver_queries.check_if_teacher_busy_at_time(
            teacher=teacher,
            starts_at=dt.time(hour=9, minute=30),
            ends_at=dt.time(hour=10, minute=30),
            day_of_week=break_.day_of_week,
        )

        # Check teacher successfully made busy
        assert clash.breaks.get() == break_

    def test_teacher_not_busy_when_has_not_commitments(self):
        teacher = data_factories.Teacher()

        # Check if busy
        clash = teacher_solver_queries.check_if_teacher_busy_at_time(
            teacher=teacher,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=constants.Day.MONDAY,
        )

        assert not clash
