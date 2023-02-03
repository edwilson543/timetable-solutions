"""Integration test for the entry-point method on the TimetableSolverConstraints class"""

# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp
import pytest

# Local application imports
from data import constants as data_constants
from domain import solver as slvr
from tests import data_factories
from tests import domain_factories


@pytest.mark.django_db
class TestSolverConstraints:
    @pytest.mark.parametrize("n_pupils", [1, 2, 3])
    def test_add_all_constraints_to_problem_with_three_slots(self, n_pupils):
        """
        Test for all constraints when we have 2 consecutive slots and 1 slot on another day,
        available to n lessons needing 1 double and 1 single.
        """
        # Set minimum necessary db content
        school = data_factories.School()

        yg = data_factories.YearGroup(school=school)
        pupils = [
            data_factories.Pupil(school=school, year_group=yg)
            for _ in range(0, n_pupils)
        ]

        # And a lesson to get some constraints for
        data_factories.Lesson(
            school=school,
            total_required_slots=3,
            total_required_double_periods=1,
            pupils=pupils,
        )

        # And 3 slots - 2 consecutive, one on another day
        slot_0 = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            starts_at=dt.time(hour=10),
            day_of_week=data_constants.Day.MONDAY,
        )
        data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)
        data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            starts_at=dt.time(hour=10),
            day_of_week=data_constants.Day.TUESDAY,
        )
        n_slots = 3

        # Set up the necessary domain components to get the constraints
        spec = domain_factories.SolutionSpecification()
        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key, solution_specification=spec
        )
        variables = slvr.TimetableSolverVariables(inputs=data)
        constraint_maker = slvr.TimetableSolverConstraints(
            inputs=data, variables=variables
        )
        dummy_problem = lp.LpProblem()

        # Now we can get the constraints
        constraint_maker.add_constraints_to_problem(problem=dummy_problem)

        # Check outcome - note the dummy_problem is modified in-place
        constraints = dummy_problem.constraints

        # Expected constraints:
        pupil = n_pupils * n_slots
        teacher = n_slots
        classroom = n_slots
        fulfilment_singles = 1  # 1 lesson
        fulfilment_doubles = 1  # 1 lesson
        dependency_doubles = 2  # Only the consecutive slots can be a double
        assert len(constraints) == (
            pupil
            + teacher
            + classroom
            + fulfilment_singles
            + fulfilment_doubles
            + dependency_doubles
        )
