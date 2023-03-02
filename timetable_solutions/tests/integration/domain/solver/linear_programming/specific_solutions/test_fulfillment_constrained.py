# Third party imports
import pulp as lp
import pytest

# Local application imports
from tests import data_factories
from tests.integration.domain.solver.linear_programming import helpers


@pytest.mark.django_db
class TestSolverSolutionFulfillmentConstrainDriven:
    """
    Tests for solver solutions where the fulfilling the required number of slots / double period
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

        # Check solutions are as expected
        assert solver_.problem.status == lp.LpStatusOptimal

        n_solved_slots = sum(solver_.variables.decision_variables.values())
        # We only needed one slot from the solution
        assert n_solved_slots == 1
