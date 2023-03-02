# Third party imports
import pulp as lp
import pytest

# Local application imports
from data.constants import Day
from domain import solver
from tests import data_factories
from tests.integration.domain.solver.linear_programming import helpers


@pytest.mark.django_db
class TestSolverSolutionFulfillmentConstrainDriven:
    """
    Tests for solver solutions where fulfilling the required number of slots
    per week is what drives the solution.
    """

    @pytest.mark.parametrize("total_required_slots", [1, 3])
    def test_required_slots_are_fulfilled(self, total_required_slots: int):
        lesson = data_factories.Lesson.with_n_pupils(
            total_required_slots=total_required_slots, total_required_double_periods=0
        )
        yg = lesson.pupils.first().year_group

        # Make one more than the total number of required slots
        for _ in range(0, total_required_slots + 1):
            data_factories.TimetableSlot(
                relevant_year_groups=(yg,), school=lesson.school
            )

        # Solve the timetabling problem
        solver_ = helpers.get_solution(lesson.school)

        # Check solutions are as expected
        assert solver_.problem.status == lp.LpStatusOptimal

        n_solved_slots = sum(solver_.variables.decision_variables.values())
        assert n_solved_slots == total_required_slots

    def test_required_slots_are_fulfilled_with_user_defined_slot(self):
        pupil = data_factories.Pupil()
        slots = [
            data_factories.TimetableSlot(
                relevant_year_groups=(pupil.year_group,), school=pupil.school
            )
            for _ in range(0, 3)
        ]
        # Make a lesson with 1 user defined slot, therefore requiring 1 solved slot
        lesson = data_factories.Lesson(
            total_required_slots=2,
            total_required_double_periods=0,
            user_defined_time_slots=(slots[0],),
            school=pupil.school,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver_ = helpers.get_solution(lesson.school)

        # Check solution fulfilled the requirements
        assert solver_.problem.status == lp.LpStatusOptimal
        n_solved_slots = sum(solver_.variables.decision_variables.values())
        # We only needed one slot from the solution
        assert n_solved_slots == 1


@pytest.mark.django_db
class TestSolverSolutionDoublePeriodFulfillmentConstrainDriven:
    """
    Tests for solver solutions where fulfilling the required number of double
    periods per week is what drives the solution.
    """

    def test_required_double_period_is_fulfilled(self):
        """
        Test scenario targeted at the double period fulfillment and dependency constraints.
        We have the following setup:
        Timetable structure:
            Monday: empty-empty;
            Tuesday: empty;
        1 Lesson, requiring:
            2 total slots;
            1 double period.
        Only 2 of the 3 timeslots are consecutive, so we must have the doubler period during these slots.
        """
        lesson = data_factories.Lesson.with_n_pupils(
            total_required_slots=2,
            total_required_double_periods=1,
        )
        yg = lesson.pupils.first().year_group
        mon_1 = data_factories.TimetableSlot(
            day_of_week=Day.MONDAY, school=lesson.school, relevant_year_groups=(yg,)
        )
        mon_2 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_1)
        tue_1 = data_factories.TimetableSlot(
            day_of_week=Day.TUESDAY, school=lesson.school, relevant_year_groups=(yg,)
        )

        # Solve the timetabling problem
        solver_ = helpers.get_solution(lesson.school)

        # Check solution is a double period on monday
        assert solver_.problem.status == lp.LpStatusOptimal
        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_1)
        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_2)
        assert not helpers.lesson_occurs_at_slot(solver_.variables, lesson, tue_1)
