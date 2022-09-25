# Local application imports
from domain.solver.linear_programming.solver_input_data import TimetableSolverInputs


class TimetableSolver:
    """
    Class to formulate and solve the timetable scheduling problem as a linear programming problem
    Likely will end up wanting separate classes for different components of the problem formulation.
    """
    def __init__(self, input_data: TimetableSolverInputs):
        self.input_data = input_data
        pass
