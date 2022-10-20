"""Integration test for the entry-point method on the TimetableSolverObjective class"""

# Standard library imports
import datetime as dt

# Django imports
from django import test

# Third party imports
import pulp as lp

# Local application imports
from domain import solver as slvr


class TestSolverConstraints(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json", "unsolved_classes.json"]

    def test_add_objective_to_problem(self):
        """
        Test that the total objective function of the timetabling problem is added to the LpProblem instance.
        No need to test how every possible SolutionSpecification configuration leads to a different objective here,
        since this is done in the unit tests.
        """
        # Set test parameters
        school_access_key = 123456
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=False,
                                          allow_triple_periods_and_above=False,
                                          optimal_free_period_time_of_day=dt.time(hour=9))
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        variables = slvr.TimetableSolverVariables(inputs=data)
        objective_maker = slvr.TimetableSolverObjective(inputs=data, variables=variables)

        dummy_problem = lp.LpProblem()  # In real life, will be the LpProblem subclass carried by TimetableSolver

        # Execute test unit
        objective_maker.add_objective_to_problem(problem=dummy_problem)

        # Check outcome - note the dummy_problem is modified in-place
        objective = dummy_problem.objective

        assert isinstance(objective, lp.LpAffineExpression)
        # The slot which occurs at the free period slot has 0 zero coefficients so isn't included, hence:
        assert len(objective) == (7 - 1) * 5 * 12  # =  (slots per day - 1) * days of week * unsolved classes
        assert objective.constant == 0.0
        assert objective.name == "total_timetabling_objective"
