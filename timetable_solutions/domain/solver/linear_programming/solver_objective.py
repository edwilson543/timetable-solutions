"""
Module defining the objective function of the timetable solving problem
"""

# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp
import numpy as np

# Local application imports
from domain.solver.solver_input_data import TimetableSolverInputs
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

    def add_objective_to_problem(self, problem: lp.LpProblem) -> None:
        """
        Method to add all constraints to the passed problem - what this class is used for outside this module.
        :param problem - an instance of pulp.LpProblem, which collects constraints/objective and solves
        :return None - since the passed problem will be modified in-place
        """
        objective = self._find_and_sum_all_objective_components()
        problem += (objective, "total_timetabling_objective")

    def _find_and_sum_all_objective_components(self) -> lp.LpAffineExpression:
        """
        Method to gather each component of the objective function, and sum them together.
        :return - total_objective - the objective function of the given school timetabling problem.
        """
        objective = lp.LpAffineExpression()
        if self._inputs.solution_specification.optimal_free_period_time_of_day is not None:
            objective += self._get_free_period_time_of_day_objective()

        return objective

    # OBJECTIVE COMPONENTS
    def _get_free_period_time_of_day_objective(self) -> lp.LpAffineExpression:
        """
        Objective component relating to the total distance in time between each class that takes place and the time the
        user has specified as optimal for free periods to happen.

        The effect is to, within the constraints, push the classes away from the slot corresponding to the optimal free
        period slot - i.e. the optimal free period time acts like an opposing magnet to all the decision variables.

        :return - objective_component - the total duration of time between the optimal free time slot and each
        decision variable.
        """
        objective_component = lp.LpAffineExpression()

        # Parameters relating to optimal free period
        repulsive_hour = self._inputs.solution_specification.optimal_free_period_time_of_day.hour
        # repulsive_time_as_delta = dt.timedelta(hours=repulsive_time.hour)

        # Parameters relating to random deviations from the optimal free period
        timetable_start, timetable_finish = self._inputs.timetable_start_finish_span_as_ints
        ideal_proportion = self._inputs.solution_specification.ideal_proportion_of_free_periods_at_this_time

        for key, var in self._decision_variables.items():
            slot_time = self._inputs.get_time_period_starts_at_from_slot_id(slot_id=key.slot_id)
            slot_time_as_delta = dt.timedelta(hours=slot_time.hour)
            difference_hours = abs(repulsive_hour - slot_time.hour)

            # To avoid all free periods taking place at the same time
            if ideal_proportion is not None:
                random_filter = np.random.random() > ideal_proportion
                # This way (1 - ideal_proportion) of slots will be randomly deviated
                if random_filter:
                    random_timetable_time = np.random.randint(timetable_start, timetable_finish)
                    random_deviation = abs(slot_time.hour - random_timetable_time)
                    difference_hours += random_deviation

            # If the associated class takes place at this time (i.e. var = 1), we will get a non-zero contribution below
            contribution = difference_hours * var
            objective_component += contribution

        return objective_component
