"""
Unit tests for the methods on the TimetableSolverObjective class.
In particular, we only test the method relating to individual objective components, and then separately test the methods
which sum all components and add them to an LpProblem in a separate integration test module
"""

# Standard library imports
import datetime as dt
from functools import lru_cache

# Third party imports
import pulp as lp

# Django imports
from django import test

# Local application imports
from domain import solver as slvr


class TestTimetableSolverObjective(test.TestCase):
    """
    Class containing the unit tests for TimetableSolverObjective's methods.
    """

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json", "unsolved_classes.json"]

    @staticmethod
    @lru_cache(maxsize=1)
    def get_objective_maker() -> slvr.TimetableSolverObjective:
        """
        Method used to instantiate the 'maker' of the objective components. Would use pytest fixtures, but this does not
        work since the test class subclasses the Django TestCase.
        """
        school_access_key = 123456
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True,
                                          optimal_free_period_time_of_day=dt.time(hour=12))  # Note this inclusion
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        variables = slvr.TimetableSolverVariables(inputs=data)
        objective_maker = slvr.TimetableSolverObjective(inputs=data, variables=variables)
        return objective_maker

    def test_get_free_period_time_of_day_objective(self):
        """
        Unit test for the objective component seeking to meet the user's stated preference for when they'd like their
        free periods to be.
        """
        # Set test parameters
        objective_maker = self.get_objective_maker()

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        # The slot which occurs at the free period slot has 0 zero coefficients so isn't included, hence:
        assert len(objective_component) == (7 - 1) * 5 * 12  # =  (slots per day - 1) * days of week * unsolved classes
        assert objective_component.constant == 0.0
