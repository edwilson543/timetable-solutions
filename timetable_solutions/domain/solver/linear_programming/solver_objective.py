"""
Module defining the objective function of the timetable solving problem
"""

# Third party imports
import pulp as lp

# Local application imports
from domain.solver.solver_input_data import TimetableSolverInputs
from domain.solver.linear_programming.solver_variables import TimetableSolverVariables, var_key


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
        pass

    def _sum_all_objective_components(self) -> lp.LpAffineExpression:
        """
        Method to gather each component of the objective function, and sum the together.
        :return - total_objective - the objective function of the given school timetabling problem.
        """
        pass

    # OBJECTIVE COMPONENTS
    def _free_period_timing_objective(self) -> lp.LpAffineExpression:
        pass
