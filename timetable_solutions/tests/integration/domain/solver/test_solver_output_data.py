"""
Integration test for the TimetableSolverOutcome
"""

# Third party imports
import pytest

# Local application imports
from domain import solver
from tests import data_factories
from tests.integration.domain.solver.linear_programming import helpers


@pytest.mark.django_db
class TestTimetableSolverOutcome:
    @pytest.mark.parametrize("total_required_slots", [1, 3])
    def test_lesson_has_solver_defined_slots_mutated(self, total_required_slots: int):
        """Solving a timetable solution should set the 'solver_defined_time_slots' on the lesson."""
        lesson = data_factories.Lesson.with_n_pupils(
            total_required_slots=total_required_slots, total_required_double_periods=0
        )
        yg = lesson.pupils.first().year_group

        # Make sufficient timetable slots to meet the required slots
        slots = {
            data_factories.TimetableSlot(
                relevant_year_groups=(yg,), school=lesson.school
            )
            for _ in range(0, total_required_slots)
        }

        # Solve the timetabling problem
        solver_ = helpers.get_solution(lesson.school)
        solver_.solve()

        # Update the db from the solution
        solver.TimetableSolverOutcome(timetable_solver=solver_)

        # Check solutions are as expected
        lesson.refresh_from_db()
        assert set(lesson.solver_defined_time_slots.all()) == slots
