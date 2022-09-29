# Third party imports
import pulp as lp

# Local application imports
from domain.solver.linear_programming.solver_input_data import TimetableSolverInputs
from domain.solver.linear_programming.solver_variables import TimetableSolverVariables


class TimetableSolver(lp.LpProblem):
    """
    Class to formulate and solve the timetable scheduling problem as a linear programming problem
    Likely will end up wanting separate classes for different components of the problem formulation.
    """
    def __init__(self,
                 input_data: TimetableSolverInputs,
                 variables: TimetableSolverVariables,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_data = input_data
        self.variables = variables
