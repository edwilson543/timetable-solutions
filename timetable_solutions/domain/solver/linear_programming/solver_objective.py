"""
Module defining the objective function of the timetable solving problem
"""

# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp
import numpy as np

# Local application imports
from domain.solver.solver_input_data import TimetableSolverInputs, SolutionSpecification
from domain.solver.linear_programming.solver_variables import TimetableSolverVariables


class TimetableSolverObjective:
    """
    Class responsible for writing the objective function, and adding it to LpProblem instances.

    The methods are grouped as follows:
    - Entry point method (add_objective_to_problem)
    - Summary method (_sum_all_objective_components)
    - Methods producing the individual components of the objective
    """
    def __init__(self,
                 inputs: TimetableSolverInputs,
                 variables: TimetableSolverVariables):
        self._inputs = inputs
        self._decision_variables = variables.decision_variables

        # Add some instance attributes for ease of access
        self._timetable_start = self._inputs.timetable_start
        self._timetable_finish = self._inputs.timetable_finish

    def add_objective_to_problem(self, problem: lp.LpProblem) -> None:
        """
        Method to add all constraints to the passed problem - what this class is used for outside this module.
        :param problem - an instance of pulp.LpProblem, which collects constraints/objective and solves
        :return None - since the passed problem will be modified in-place
        """
        objective = self._get_free_period_time_of_day_objective()
        problem += (objective, "total_timetabling_objective")

    def _get_free_period_time_of_day_objective(self) -> lp.LpAffineExpression:
        """
        The objective function is the total distance in time between each class that takes place and the time the
        user has specified as optimal for free periods to happen (give or take some randomness, see below)

        The effect is to, within the constraints, push the classes away from the slot corresponding to the optimal free
        period slot, the 'repulsive_time'.
        i.e. the optimal free period time acts like an opposing magnet to all the decision variables.

        :return - objective_component - the total duration of time between the optimal free time slot and each
        decision variable.
        """
        objective_component = lp.LpAffineExpression()

        for key, variable in self._decision_variables.items():
            # Get the time of the slot corresponding to the variable
            slot_time = self._inputs.get_time_period_starts_at_from_slot_id(slot_id=key.slot_id)
            slot_time_as_delta = dt.timedelta(hours=slot_time.hour)

            repulsive_time = self._get_optimal_free_period_time()
            difference_hours = abs(repulsive_time - slot_time.hour)

            # If variable.varValue = 1 (i.e. the associated class takes place at this time in the solution)
            # then we get a non-zero contribution below
            contribution = difference_hours * variable
            objective_component += contribution

        return objective_component

    # ANCILLARY METHODS
    def _get_optimal_free_period_time(self) -> float:
        """
        Method to get the optimal free period times - the times at which we avoid putting classes at, because we want
        free periods at these time.
        The logic for getting the optimal fre period depends heavily on the SolutionSpecification, hence the need for
        the series of methods below, declared within the if/elif chain.
        :return: optimal_free_period_time - float representing the time of day when we don't want to put a class, (for
        the given call to this method only - note that this method is called once for each variable, and hence each
        variable can have its own optimal free period time.)
        """
        initial_optimal_free_period_time = self._inputs.solution_specification.optimal_free_period_time_of_day
        if isinstance(initial_optimal_free_period_time, dt.time):
            optimal_free_period_time = self._get_optimal_free_period_time_specified_time()
        elif initial_optimal_free_period_time == SolutionSpecification.OptimalFreePeriodOptions.NONE:
            optimal_free_period_time = self._get_optimal_free_period_time_no_specified_time()
        elif initial_optimal_free_period_time == SolutionSpecification.OptimalFreePeriodOptions.MORNING:
            optimal_free_period_time = self._get_optimal_free_period_time_morning_specified()
        elif initial_optimal_free_period_time == SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON:
            optimal_free_period_time = self._get_optimal_free_period_time_afternoon_specified()
        else:
            raise ValueError(f"{initial_optimal_free_period_time} is not a valid value for the optimal free period "
                             f"time and hence cannot be used to get a repulsive hour.")
        return optimal_free_period_time

    # METHODS PROVIDING THE LOGIC TO GET THE OPTIMAL FREE PERIOD IN EACH SOLUTION SPECIFICATION SCENARIO
    def _get_optimal_free_period_time_no_specified_time(self) -> float:
        """
        Method randomly generating a time between timetable_start-timetable_finish to avoid putting classes at,
        to encourage free periods at this time.
        This is used when a time has not been specified as optimal (i.e. the user has no preference).
        :return - optimal_free_period_time - float representing the hour on the 24 hour

        Note that the ideal proportion parameter is not relevant in this case, since all hours are generated randomly.
        Note also that a different random value is generated for each variable
        """
        optimal_free_period_time = np.random.uniform(low=self._timetable_start, high=self._timetable_finish)
        return optimal_free_period_time

    def _get_optimal_free_period_time_specified_time(self):
        """
        Method that ideal_proportion % of the time will just return the user-specified optimal free period time (the
        repulsive hour), and the 1 - this % of times, return a random float  between timetable_start / timetable_finish
        :return - optimal_free_period_time - float representing the hour on the 24 hour
        """
        # With probability (1 - ideal_proportion) we randomly generate a repulsive hour (otherwise return user spec.)
        ideal_proportion = self._inputs.solution_specification.ideal_proportion_of_free_periods_at_this_time
        generate_random_repulsive_hour = np.random.random() > ideal_proportion

        if generate_random_repulsive_hour:
            optimal_free_period_time = np.random.uniform(low=self._timetable_start, high=self._timetable_finish)
        else:
            optimal_free_period_time = self._inputs.solution_specification.optimal_free_period_time_of_day.hour
        return optimal_free_period_time

    def _get_optimal_free_period_time_morning_specified(self) -> float:
        pass

    def _get_optimal_free_period_time_afternoon_specified(self) -> float:
        pass
