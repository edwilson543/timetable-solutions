# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp
import pytest

# Local application imports
from data import constants as data_constants
from tests import data_factories
from tests.integration.domain.solver.linear_programming import helpers


@pytest.mark.django_db
class TestSolverSolutionTeacherConstraintDriven:
    """Tests for solver solutions where the availability of a teacher drives the solution."""

    def test_teacher_is_only_allocated_one_lesson_at_a_time(self):
        """
        A teacher must teach 2 lessons.
        Both use 1 slot, and there are 2 possible time slots.
        """
        teacher = data_factories.Teacher()
        pupil = data_factories.Pupil(school=teacher.school)
        slot_1 = data_factories.TimetableSlot(
            school=teacher.school,
            relevant_year_groups=(pupil.year_group,),
        )
        slot_2 = data_factories.TimetableSlot(
            school=teacher.school,
            relevant_year_groups=(pupil.year_group,),
        )
        # Male two lessons and allocate both to the same teacher
        lesson_a = data_factories.Lesson(
            school=teacher.school,
            total_required_slots=1,
            total_required_double_periods=0,
            teacher=teacher,
            pupils=(pupil,),
        )
        lesson_b = data_factories.Lesson(
            school=teacher.school,
            total_required_slots=1,
            total_required_double_periods=0,
            teacher=teacher,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver_ = helpers.get_solution(teacher.school)

        # Check solution allows teacher to both lessons
        assert solver_.problem.status == lp.LpStatusOptimal

        la_1 = helpers.lesson_occurs_at_slot(solver_.variables, lesson_a, slot_1)
        la_2 = helpers.lesson_occurs_at_slot(solver_.variables, lesson_a, slot_2)
        lb_1 = helpers.lesson_occurs_at_slot(solver_.variables, lesson_b, slot_1)
        lb_2 = helpers.lesson_occurs_at_slot(solver_.variables, lesson_b, slot_2)
        assert (la_1 and not lb_1) or (la_2 and not lb_2)
        assert (lb_1 and not la_1) or (lb_2 and not la_2)

    def test_teacher_is_only_allocated_one_lesson_at_a_time_when_has_fixed_slot(self):
        """
        A teacher must teach 2 lessons.
        Both use 1 slot, there are 2 possible time slots,
        one lesson is fixed at one of the slots.
        """
        teacher = data_factories.Teacher()
        pupil = data_factories.Pupil(school=teacher.school)
        slot_1 = data_factories.TimetableSlot(
            school=teacher.school,
            relevant_year_groups=(pupil.year_group,),
        )
        slot_2 = data_factories.TimetableSlot(
            school=teacher.school,
            relevant_year_groups=(pupil.year_group,),
        )
        # Male two lessons and allocate both to the same teacher
        data_factories.Lesson(
            school=teacher.school,
            total_required_slots=1,
            total_required_double_periods=0,
            teacher=teacher,
            pupils=(pupil,),
            user_defined_time_slots=(slot_1,),
        )
        lesson_2 = data_factories.Lesson(
            school=teacher.school,
            total_required_slots=1,
            total_required_double_periods=0,
            teacher=teacher,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver_ = helpers.get_solution(teacher.school)

        # Check solution allows teacher to both lessons
        assert solver_.problem.status == lp.LpStatusOptimal

        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson_2, slot_2)

    @pytest.mark.parametrize("clash_slot_overlap_minutes", [0, 30])
    def test_teacher_has_two_year_groups_at_clashing_times(
        self, clash_slot_overlap_minutes: int
    ):
        """
        One teacher takes two lessons each requiring one slot.
        The first lesson only has one slot choice for when it can go.
        The second slot has two choices of slot, but one clashes with the first lesson's only choice.
        Since the teacher can only be in one place at a time, the second lesson is determined.
        """
        teacher = data_factories.Teacher()

        # Make a lesson with only 1 slot choice
        lesson_1 = data_factories.Lesson.with_n_pupils(
            teacher=teacher,
            school=teacher.school,
            total_required_slots=1,
            total_required_double_periods=0,
        )
        yg_1 = lesson_1.pupils.first().year_group
        slot_1 = data_factories.TimetableSlot(
            relevant_year_groups=(yg_1,),
            school=teacher.school,
            day_of_week=data_constants.Day.MONDAY,
        )

        # Make a lesson with 2 slot choices, once clashing with slot_1
        lesson_2 = data_factories.Lesson.with_n_pupils(
            teacher=teacher,
            school=teacher.school,
            total_required_slots=1,
            total_required_double_periods=0,
        )
        yg_2 = lesson_2.pupils.first().year_group
        slot_1_clash = data_factories.TimetableSlot(
            relevant_year_groups=(yg_2,),
            school=teacher.school,
            starts_at=dt.time(
                hour=slot_1.starts_at.hour, minute=clash_slot_overlap_minutes
            ),
            ends_at=dt.time(
                hour=slot_1.ends_at.hour, minute=clash_slot_overlap_minutes
            ),
            day_of_week=data_constants.Day.MONDAY,
        )
        lesson_2_forced_slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg_2,),
            school=teacher.school,
            starts_at=slot_1.starts_at,
            ends_at=slot_1.ends_at,
            day_of_week=data_constants.Day.TUESDAY,  # Note different day
        )

        # Solve the problem for this school
        solver_ = helpers.get_solution(school=teacher.school)

        # Check solved & solution as expected
        assert solver_.problem.status == lp.LpStatusOptimal

        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson_1, slot_1)
        assert helpers.lesson_occurs_at_slot(
            solver_.variables, lesson_2, lesson_2_forced_slot
        )
        assert not helpers.lesson_occurs_at_slot(
            solver_.variables, lesson_2, slot_1_clash
        )
