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
import pytest

# Local application imports
from domain import solver as slvr
from tests import data_factories
from tests import domain_factories


@pytest.mark.django_db
class TestTimetableSolverObjectiveGetFreePeriodTimeOfDayObjective:
    """
    Class containing the unit tests for TimetableSolverObjective's methods.
    """

    # --------------------
    # Helpers
    # --------------------

    def get_objective_maker(
        self,
        solution_spec: slvr.SolutionSpecification,
    ) -> slvr.TimetableSolverObjective:
        """
        Method used to instantiate the 'maker' of the objective components. Would use pytest fixtures, but this does not
        work since the test class subclasses the Django TestCase.
        """
        data = slvr.TimetableSolverInputs(
            school_id=self.school.school_access_key,
            solution_specification=solution_spec,
        )
        variables = slvr.TimetableSolverVariables(inputs=data)
        objective_maker = slvr.TimetableSolverObjective(
            inputs=data, variables=variables
        )
        return objective_maker

    def set_single_lesson_for_school(self) -> None:
        """
        Create one lesson for a school, with the necessary pupil and year group.
        Note that this lesson only requires a single slot.

        All tests use this method (and call it per test, to get new data).
        """

        self.school = data_factories.School()

        self.yg = data_factories.YearGroup(school=self.school)
        self.pupil = data_factories.Pupil(school=self.school, year_group=self.yg)

        self.lesson = data_factories.Lesson(
            school=self.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(self.pupil,),
        )

    # --------------------
    # Tests
    # --------------------

    def test_no_optimal_free_period_time(self):

        self.set_single_lesson_for_school()
        # Make a single slot to contribute to the objective
        slot = data_factories.TimetableSlot(
            school=self.school, relevant_year_groups=(self.yg,)
        )

        # Set the optimal free time to NONE
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=slvr.SolutionSpecification.OptimalFreePeriodOptions.NONE,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Get the objective, and track how many objective contributions were uniformly generated
        with mock.patch("numpy.random.uniform", return_value=0) as mock_random_uniform:
            objective_component = (
                objective_maker._get_free_period_time_of_day_objective()
            )
            assert mock_random_uniform.call_count == 1

        # Expect one component of the expression for our single slot
        assert len(objective_component) == 1
        assert objective_component.constant == 0.0

        # The coefficients should be the difference between the slot start times
        # and the mocked return value (which is 0), so should the starts times
        assert list(objective_component.values()) == [slot.period_starts_at.hour]

    def test_optimal_free_period_is_always_same_time(
        self,
    ):
        self.set_single_lesson_for_school()

        # Make two consecutive slots
        slot_0 = data_factories.TimetableSlot(
            school=self.school, relevant_year_groups=(self.yg,)
        )
        slot_1 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)

        # Set the optimal free period time at the start of the first slot
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=slot_0.period_starts_at,
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Get the objective, and ensure no randomness was involved
        with mock.patch("numpy.random.uniform") as mock_random_uniform:
            objective_component = (
                objective_maker._get_free_period_time_of_day_objective()
            )
            mock_random_uniform.assert_not_called()

        # Expect 1 variable only in the expression, since 1 of the 2 slots is at the optimal time
        assert len(objective_component) == 1
        assert objective_component.constant == 0.0

        # The second of the consecutive slots is 1 hour from the optimal time
        assert list(objective_component.values()) == [
            slot_1.period_starts_at.hour - slot_0.period_starts_at.hour
        ]

    def test_optimal_free_period_is_fifty_percent_same_time(
        self,
    ):
        self.set_single_lesson_for_school()

        # Make two consecutive slots
        slot_0 = data_factories.TimetableSlot(
            school=self.school, relevant_year_groups=(self.yg,)
        )
        slot_1 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)

        # Set the optimal free period time at a time neither of the slots are at
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=dt.time(
                hour=slot_1.period_starts_at.hour + 1
            ),
            ideal_proportion_of_free_periods_at_this_time=0.5,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Both slots should always contribute something to the objective
        assert len(objective_component) == 2
        assert objective_component.constant == 0.0

    @pytest.mark.parametrize(
        "optimal_free_period_time",
        [
            slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING,
            slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON,
        ],
    )
    def test_optimal_time_is_morning_or_afternoon(self, optimal_free_period_time):
        self.set_single_lesson_for_school()

        # Make one slot in the morning, one in the afternoon
        morning_slot = data_factories.TimetableSlot(
            period_starts_at=dt.time(hour=9),
            period_ends_at=dt.time(hour=10),
            school=self.school,
            relevant_year_groups=(self.yg,),
        )
        afternoon_slot = data_factories.TimetableSlot(
            period_starts_at=dt.time(hour=15),
            period_ends_at=dt.time(hour=16),
            school=self.school,
            relevant_year_groups=(self.yg,),
        )

        # Get a spec always favouring the parameterised time
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=optimal_free_period_time,
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )

        # Get the objective
        objective_maker = self.get_objective_maker(solution_spec=spec)
        objective_component = objective_maker._get_free_period_time_of_day_objective()

        # Both slots should contribute to the objective
        assert len(objective_component) == 2
        assert objective_component.constant == 0.0

        morning_slot_contribution = [
            coeff
            for var, coeff in objective_component.items()
            if str(morning_slot.slot_id) in var.name
        ][0]
        afternoon_slot_contribution = [
            coeff
            for var, coeff in objective_component.items()
            if str(afternoon_slot.slot_id) in var.name
        ][0]

        # Check the slot at the time of day which isn't optimal had the higher contribution
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        if optimal_free_period_time == morning:
            assert morning_slot_contribution < afternoon_slot_contribution
        else:
            assert afternoon_slot_contribution < morning_slot_contribution


class TestTimetableSolverObjectiveGetOptimalFreePeriodTime(
    TestTimetableSolverObjectiveGetFreePeriodTimeOfDayObjective
):
    """Tests for the methods getting the optimal free periods in each different scenario."""

    def test_no_specified_time_gives_random_time_between_start_and_finish(self):
        self.set_single_lesson_for_school()

        # Make a low / high slot
        slot_0 = data_factories.TimetableSlot(
            school=self.school,
            relevant_year_groups=(self.yg,),
        )
        slot_1 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)

        # Set a spec with no optimal time
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=slvr.SolutionSpecification.OptimalFreePeriodOptions.NONE
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Get the optimal free time, given our slots and spec
        opt_time = objective_maker._get_optimal_free_period_time_no_specified_time()

        # Check outcome
        assert slot_0.period_starts_at.hour <= opt_time <= slot_1.period_ends_at.hour

    def test_specified_time_guarantees_no_random_return(
        self,
    ):
        """
        Unit test for returning the user-specified optimal free period - setting the ideal proportion to 1.0 ensures
        that we do not get a random return.
        """
        self.set_single_lesson_for_school()
        # Need at least one slot to be able to do anything
        data_factories.TimetableSlot(
            school=self.school, relevant_year_groups=(self.yg,)
        )

        # Set test parameters
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=dt.time(hour=9),
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Get the optimal time, and ensure no randomness was involved
        with mock.patch("numpy.random.uniform") as mock_random_uniform:
            opt_time = objective_maker._get_optimal_free_period_time()
            mock_random_uniform.assert_not_called()

        # Optimal time should just be the spec
        assert opt_time == 9

    def test_specified_time_guaranteed_random_return_using_patch(
        self,
    ):
        """
        Unit test for returning the user-specified optimal free period - setting the ideal proportion to 1.0 ensures
        that we do not get a random return.
        """
        self.set_single_lesson_for_school()
        # Need at least one slot to be able to do anything
        slot = data_factories.TimetableSlot(
            school=self.school, relevant_year_groups=(self.yg,)
        )

        ideal_prop = 0.75
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=dt.time(hour=9),
            ideal_proportion_of_free_periods_at_this_time=ideal_prop,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Ensure return value > ideal_proportion
        with mock.patch("numpy.random.random", return_value=ideal_prop + 0.01):
            opt_time = objective_maker._get_optimal_free_period_time()

        # Opt time should be randomly generated
        assert slot.period_starts_at.hour < opt_time <= slot.period_ends_at.hour

    def test_morning_always_optimal_guarantees_random_morning_return(
        self,
    ):
        self.set_single_lesson_for_school()
        # Make a slot in the morning
        slot = data_factories.TimetableSlot(
            school=self.school,
            relevant_year_groups=(self.yg,),
            period_starts_at=dt.time(hour=9),
        )

        # Get optimal time when optimal is the morning
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=morning,
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        opt_time = objective_maker._get_optimal_free_period_time()

        # Check optimal time within morning hours
        assert slot.period_starts_at.hour <= opt_time <= 12

    def test_morning_specified_can_still_give_random_afternoon_return_using_patch(
        self,
    ):
        self.set_single_lesson_for_school()
        # Make a slot in the afternoon
        slot = data_factories.TimetableSlot(
            school=self.school,
            relevant_year_groups=(self.yg,),
            period_ends_at=dt.time(hour=17),
        )

        # Get optimal time when optimal is the morning
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        ideal_prop = 0.5
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=morning,
            ideal_proportion_of_free_periods_at_this_time=ideal_prop,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit, ensuring return value > ideal_proportion
        with mock.patch("numpy.random.random", return_value=ideal_prop + 0.01):
            opt_time = objective_maker._get_optimal_free_period_time()

        # Check optimal time randomly set to afternoon
        assert 12 <= opt_time <= slot.period_ends_at.hour

    def test_afternoon_always_optimal_guarantees_random_morning_return(
        self,
    ):
        self.set_single_lesson_for_school()
        # Make a slot in the afternoon
        slot = data_factories.TimetableSlot(
            school=self.school,
            relevant_year_groups=(self.yg,),
            period_ends_at=dt.time(hour=17),
        )

        # Get optimal time when optimal is the morning
        afternoon = slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=afternoon,
            ideal_proportion_of_free_periods_at_this_time=1.0,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit
        opt_time = objective_maker._get_optimal_free_period_time()

        # Check optimal time within morning hours
        assert 12 <= opt_time <= slot.period_ends_at.hour

    def test_get_optimal_free_period_time_morning_specified_guaranteed_random_morning_return_using_patch(
        self,
    ):
        self.set_single_lesson_for_school()
        # Make a slot in the morning
        slot = data_factories.TimetableSlot(
            school=self.school,
            relevant_year_groups=(self.yg,),
            period_starts_at=dt.time(hour=9),
        )

        # Get optimal time when optimal is the morning
        afternoon = slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON
        ideal_prop = 0.5
        spec = domain_factories.SolutionSpecification(
            optimal_free_period_time_of_day=afternoon,
            ideal_proportion_of_free_periods_at_this_time=ideal_prop,
        )
        objective_maker = self.get_objective_maker(solution_spec=spec)

        # Execute test unit, ensuring return value > ideal_proportion
        with mock.patch("numpy.random.random", return_value=ideal_prop + 0.01):
            opt_time = objective_maker._get_optimal_free_period_time()

        # Check optimal time randomly set to morning
        assert slot.period_starts_at.hour <= opt_time <= 12
