# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data.constants import Day
from domain import solver
from tests import data_factories, domain_factories


@pytest.mark.django_db
class TestSolverSolutionObjectiveDriven:
    """
    Tests for solver solutions where the presence of a non-zero
    objective function is what drives the solution.
    """

    def test_optimal_free_period_in_morning_pushes_lesson_to_end_of_day(self):
        """
        Test scenario targeted at using the optimal free period objective component, with a specific time of day.
        We have the following setup:
        Timetable structure:
            Some day: empty-empty;
        1 Lesson, requiring:
            1 slot;
        Optimal free period time:
            Slot 1;
        Since the optimal free period slot pushes slots away from it as much as possible, we expect the 1 slot to take
        place at slot 4.
        """
        pupil = data_factories.Pupil()
        yg = pupil.year_group
        slot_1 = data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(yg,),
        )
        slot_2 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_1)
        lesson = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )

        # Make the optimal free period time when the first slot is
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=slot_1.starts_at,
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=lesson.school.school_access_key,
            solution_specification=spec,
        )

        # Check the lesson now has the solution set
        assert lesson.solver_defined_time_slots.get() == slot_2
