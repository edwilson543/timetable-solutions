"""Integration test for running the solver end-to-end."""

# Third party imports
import pytest

# Local application imports
from domain.solver.run_solver import produce_timetable_solutions
from tests import data_factories, domain_factories


@pytest.mark.django_db
class TestProduceTimetableSolutions:
    def test_school_with_complete_inputs_gets_solution(self):
        """
        Test that the solver can run end-to-end.
        The solver should be able to load the required data, produce a timetable solution,
        and then save it in the database.
        """
        # Create some school data
        pupil = data_factories.Pupil()
        data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        lesson = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )

        # Try to find a solutions
        error_messages = produce_timetable_solutions(
            school_access_key=pupil.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Check a solution was produced
        assert len(error_messages) == 0
        assert lesson.solver_defined_time_slots.count() == 1

    # TODO -> test some error paths
