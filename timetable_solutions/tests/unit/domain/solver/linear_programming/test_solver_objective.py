"""
Unit tests for the methods on the TimetableSolverObjective class.
In particular, we test:
- The methods calculating the entire objective function, in different solution specification scenarios
- The methods calculating individual random optimal free periods, each using different logic
"""

# Standard library imports
import datetime as dt
from unittest import mock

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

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "pupils.json",
        "teachers.json",
        "timetable.json",
        "lessons_without_solution",
    ]

    @staticmethod
    def get_objective_maker(
        solution_spec: slvr.SolutionSpecification,
    ) -> slvr.TimetableSolverObjective:
        """
        Method used to instantiate the 'maker' of the objective components. Would use pytest fixtures, but this does not
        work since the test class subclasses the Django TestCase.
        """
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=solution_spec
        )
        variables = slvr.TimetableSolverVariables(inputs=data)
        objective_maker = slvr.TimetableSolverObjective(
            inputs=data, variables=variables
        )
        return objective_maker

    # TESTS FOR THE HIGH-LEVEL METHOD CALCULATING THE TOTAL OBJECTIVE
    def test_get_free_period_time_of_day_objective_optimal_free_period_is_no_preference(
        self,
    ):
        """
        Unit test for the objective when the no specific time is optimal for the free periods
        """
        # Set test parameters
        opt_free_period = slvr.SolutionSpecification.OptimalFreePeriodOptions.NONE
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=opt_free_period,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        assert (
            len(objective_component) == 7 * 5 * 12
        )  # slots per day * days of week * unsolved classes
        assert objective_component.constant == 0.0

    def test_get_free_period_time_of_day_objective_optimal_free_period_is_always_same_time(
        self,
    ):
        """
        Unit test for the objective when a specific time is optimal for free periods
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=dt.time(hour=12),
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        # The slot which occurs at the free period slot has 0 zero coefficients so isn't included, hence:
        assert (
            len(objective_component) == (7 - 1) * 5 * 12
        )  # =  (slots per day - 1) * days of week * unsolved classes
        assert objective_component.constant == 0.0

    def test_get_free_period_time_of_day_objective_optimal_free_period_is_fifty_percent_same_time(
        self,
    ):
        """
        Unit test for the objective when 50% of the free periods would ideally be at a specific time period
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=dt.time(hour=12),
            ideal_proportion_of_free_periods_at_this_time=0.5,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        assert (
            len(objective_component) >= (7 - 1) * 5 * 12
        )  # Equal to corresponds to no successful random generation
        assert objective_component.constant == 0.0

    def test_get_free_period_time_of_day_objective_optimal_free_period_is_morning(self):
        """
        Unit test for the objective when the morning is optimal for the free periods
        """
        # Set test parameters
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=morning,
            ideal_proportion_of_free_periods_at_this_time=0.75,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        assert (
            len(objective_component) == 7 * 5 * 12
        )  # slots per day * days of week * unsolved classes
        assert objective_component.constant == 0.0

    def test_get_free_period_time_of_day_objective_optimal_free_period_is_afternoon(
        self,
    ):
        """
        Unit test for the objective when the afternoon is optimal for the free periods
        """
        # Set test parameters
        afternoon = slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=afternoon,
            ideal_proportion_of_free_periods_at_this_time=0.75,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Check outcome
        assert isinstance(objective_component, lp.LpAffineExpression)
        assert (
            len(objective_component) == 7 * 5 * 12
        )  # slots per day * days of week * unsolved classes
        assert objective_component.constant == 0.0

    # TESTS FOR THE INDIVIDUAL METHODS PROVIDING EACH PIECE OF LOGIC
    def test_get_optimal_free_period_time_no_specified_time(self):
        """
        Unit test for getting a random time of day between the timetable start and finish
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day="NOT-USED-IN-TEST",
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        opt_time = objective_maker._get_optimal_free_period_time_no_specified_time()

        # Check outcome
        assert 9 <= opt_time <= 17

    def test_get_optimal_free_period_time_specified_time_guaranteed_no_random_return(
        self,
    ):
        """
        Unit test for returning the user-specified optimal free period - setting the ideal proportion to 1.0 ensures
        that we do not get a random return.
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=dt.time(hour=9),
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        opt_time = objective_maker._get_optimal_free_period_time()

        # Check outcome
        assert opt_time == 9  # See test parameters

    def test_get_optimal_free_period_time_specified_time_guaranteed_random_return_using_patch(
        self,
    ):
        """
        Unit test for returning the user-specified optimal free period - setting the ideal proportion to 1.0 ensures
        that we do not get a random return.
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=dt.time(hour=9),
            ideal_proportion_of_free_periods_at_this_time=0.75,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        with mock.patch(
            "numpy.random.random", return_value=0.8
        ):  # Ensure return value > ideal_proportion
            opt_time = objective_maker._get_optimal_free_period_time()

        # Check outcome
        assert (
            opt_time != 9
        )  # Should be randomly generated (probability of hitting from uniform d is nearly zero)
        assert 9 < opt_time <= 17

    def test_get_optimal_free_period_time_morning_specified_guaranteed_random_morning_return(
        self,
    ):
        """
        Unit test for returning a random optimal free period in the morning - setting the ideal proportion to
        1.0 ensures that we do not get the opposite return (afternoon).
        """
        # Set test parameters
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=morning,
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        opt_time = objective_maker._get_optimal_free_period_time()

        # Check outcome
        assert 9 <= opt_time <= 12  # Morning hours

    def test_get_optimal_free_period_time_morning_specified_guaranteed_random_afternoon_return_using_patch(
        self,
    ):
        """
        Unit test for returning a random optimal free period in the afternoon, but when the morning is specified as
        optimal (coming about via the random generation and comparison with the ideal_proportion)
        """
        # Set test parameters
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=morning,
            ideal_proportion_of_free_periods_at_this_time=0.5,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        with mock.patch(
            "numpy.random.random", return_value=0.6
        ):  # Ensure return value > ideal_proportion
            opt_time = objective_maker._get_optimal_free_period_time()

        # Check outcome
        assert 12 <= opt_time <= 17  # Afternoon hours

    def test_get_optimal_free_period_time_afternoon_specified_guaranteed_random_afternoon_return(
        self,
    ):
        """
        Unit test for returning a random optimal free period in the afternoon - setting the ideal proportion to
        1.0 ensures that we do not get the opposite return (morning).
        """
        # Set test parameters
        afternoon = slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=afternoon,
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        opt_time = objective_maker._get_optimal_free_period_time()

        # Check outcome
        assert 12 <= opt_time <= 17  # Afternoon hours

    def test_get_optimal_free_period_time_morning_specified_guaranteed_random_morning_return_using_patch(
        self,
    ):
        """
        Unit test for returning a random optimal free period in the morning, but when the afternoon is specified as
        optimal (coming about via the random generation and comparison with the ideal_proportion)
        """
        # Set test parameters
        afternoon = slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
            optimal_free_period_time_of_day=afternoon,
            ideal_proportion_of_free_periods_at_this_time=0.5,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        with mock.patch(
            "numpy.random.random", return_value=0.6
        ):  # Ensure return value > ideal_proportion
            opt_time = objective_maker._get_optimal_free_period_time()

        # Check outcome
        assert 9 <= opt_time <= 12  # Morning hours
