"""Integration test for the entry-point method on the TimetableSolverObjective class"""

# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp
import pytest

# Local application imports
from domain import solver as slvr
from tests import data_factories
from tests import domain_factories


@pytest.mark.django_db
class TestSolverObjective:
    @pytest.mark.parametrize(
        "optimal_free_period_time",
        [
            slvr.SolutionSpecification.OptimalFreePeriodOptions.NONE,
            slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING,
            slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON,
            dt.time(hour=17),
        ],
    )
    def test_add_objective_to_problem(self, optimal_free_period_time):
        # Make some test data
        school = data_factories.School()

        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        data_factories.Lesson(
            school=school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )
        slot_0 = data_factories.TimetableSlot(
            school=school, relevant_year_groups=(yg,), period_starts_at=dt.time(hour=10)
        )
        data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)

        # Set our solution specification
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=optimal_free_period_time
        )

        # Gather our solver components
        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key, solution_specification=spec
        )
        variables = slvr.TimetableSolverVariables(inputs=data)
        objective_maker = slvr.TimetableSolverObjective(
            inputs=data, variables=variables
        )
        dummy_problem = lp.LpProblem()

        # Make and add the objective
        objective_maker.add_objective_to_problem(problem=dummy_problem)

        # Check outcome - note the dummy_problem is modified in-place
        objective = dummy_problem.objective

        # We made 2 slots, so expect the objective to be length 2
        assert len(objective) == 2
        assert objective.constant == 0.0
        assert objective.name == "total_timetabling_objective"
