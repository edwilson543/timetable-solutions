# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp
import pytest

# Local application imports
from data.constants import Day
from tests import data_factories
from tests.integration.domain.solver.linear_programming import helpers


@pytest.mark.django_db
class TestSolverSolutionPupilConstraintDriven:
    """Tests for solver solutions where the availability of a pupil drives the solution."""

    def test_pupil_is_only_allocated_one_lesson_at_a_time(self):
        """
        There is one pupil, who must go to 2 classes.
        There are 2 time slots. There are no user defined time slots, or other constraints.
        """
        pupil = data_factories.Pupil()
        slot_1 = data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        slot_2 = data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        # Male two lessons put the pupil in both of them
        lesson_a = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )
        lesson_b = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver_ = helpers.get_solution(pupil.school)

        # Check solution allows pupil to attend both lessons
        assert solver_.problem.status == lp.LpStatusOptimal

        la_1 = helpers.lesson_occurs_at_slot(solver_.variables, lesson_a, slot_1)
        la_2 = helpers.lesson_occurs_at_slot(solver_.variables, lesson_a, slot_2)
        lb_1 = helpers.lesson_occurs_at_slot(solver_.variables, lesson_b, slot_1)
        lb_2 = helpers.lesson_occurs_at_slot(solver_.variables, lesson_b, slot_2)
        assert (la_1 and not lb_1) or (la_2 and not lb_2)
        assert (lb_1 and not la_1) or (lb_2 and not la_2)

    def test_pupil_is_only_allocated_one_lesson_at_a_time_when_has_fixed_slot(self):
        """
        There is one pupil, who must go to 2 classes.
        There are 2 time slots, and one of the lessons is fixed at one of these.
        """
        pupil = data_factories.Pupil()
        slot_1 = data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        slot_2 = data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        # Male two lessons our pupil must be able to attend
        data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
            user_defined_time_slots=(slot_1,),
        )
        lesson_2 = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver_ = helpers.get_solution(pupil.school)

        # Check the second lesson was put at the second slot
        assert solver_.problem.status == lp.LpStatusOptimal

        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson_2, slot_2)
