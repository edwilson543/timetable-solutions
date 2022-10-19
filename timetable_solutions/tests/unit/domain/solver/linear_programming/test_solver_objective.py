"""
Unit tests for the methods on the TimetableSolverObjective class.
In particular, we only test the method relating to individual objective components, and then separately test the methods
which sum all components and add them to an LpProblem in a separate integration test module
"""

# Standard library imports
import datetime as dt

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
    def get_objective_maker(solution_spec: slvr.SolutionSpecification) -> slvr.TimetableSolverObjective:
        """
        Method used to instantiate the 'maker' of the objective components. Would use pytest fixtures, but this does not
        work since the test class subclasses the Django TestCase.
        """
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=solution_spec)
        variables = slvr.TimetableSolverVariables(inputs=data)
        objective_maker = slvr.TimetableSolverObjective(inputs=data, variables=variables)
        return objective_maker

    # TESTS FOR THE HIGH-LEVEL ENTRY POINT METHOD
    def test_get_free_period_time_of_day_objective_optimal_free_period_is_no_pereference(self):
        """
        Unit test for the objective when the user has requested a specific time
        """
        # Set test parameters
        opt_free_period = slvr.SolutionSpecification.OptimalFreePeriodOptions.NONE
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True,
                                          optimal_free_period_time_of_day=opt_free_period)
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        assert len(objective_component) == 7 * 5 * 12  # slots per day * days of week * unsolved classes
        assert objective_component.constant == 0.0

    def test_get_free_period_time_of_day_objective_optimal_free_period_is_always_same_time(self):
        """
        Unit test for the objective when the user has requested a specific time
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True,
                                          optimal_free_period_time_of_day=dt.time(hour=12),
                                          ideal_proportion_of_free_periods_at_this_time=1.0)
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        # The slot which occurs at the free period slot has 0 zero coefficients so isn't included, hence:
        assert len(objective_component) == (7 - 1) * 5 * 12  # =  (slots per day - 1) * days of week * unsolved classes
        assert objective_component.constant == 0.0

    def test_get_free_period_time_of_day_objective_optimal_free_period_is_fifty_percent_same_time(self):
        """
        Unit test for the objective when the user has requested a specific time
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True,
                                          optimal_free_period_time_of_day=dt.time(hour=12),
                                          ideal_proportion_of_free_periods_at_this_time=0.5)
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        assert len(objective_component) >= (7 - 1) * 5 * 12  # Equal to corresponds to no successful random generation
        assert objective_component.constant == 0.0

    def test_get_free_period_time_of_day_objective_optimal_free_period_is_morning(self):
        """
        Unit test for the objective when the user has requested a specific time
        """
        # Set test parameters
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True,
                                          optimal_free_period_time_of_day=morning,
                                          ideal_proportion_of_free_periods_at_this_time=0.75)
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        assert len(objective_component) == 7 * 5 * 12  # slots per day * days of week * unsolved classes
        assert objective_component.constant == 0.0

    def test_get_free_period_time_of_day_objective_optimal_free_period_is_afternoon(self):
        """
        Unit test for the objective when the user has requested a specific time
        """
        # Set test parameters
        afternoon = slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True,
                                          optimal_free_period_time_of_day=afternoon,
                                          ideal_proportion_of_free_periods_at_this_time=0.75)
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        assert len(objective_component) == 7 * 5 * 12  # slots per day * days of week * unsolved classes
        assert objective_component.constant == 0.0

    # TESTS FOR THE INDIVIDUAL METHODS PROVIDING EACH PIECE OF LOGIC