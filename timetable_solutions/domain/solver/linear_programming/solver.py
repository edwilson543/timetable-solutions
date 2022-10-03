# Third party imports
import pulp as lp

# Local application imports
from domain.solver.linear_programming.solver_input_data import TimetableSolverInputs
from domain.solver.linear_programming.solver_constraints import TimetableSolverConstraints
from domain.solver.linear_programming.solver_variables import TimetableSolverVariables


class TimetableSolver:
    """
    Class to formulate and solve the timetable scheduling problem as a linear programming problem.
    Subclass of the pulp LpProblem class to allow use of solve method
    """
    def __init__(self,
                 input_data: TimetableSolverInputs):
        """
        :param - input_data - passing this to __init__ triggers the formulation of the timetable solution problem as
        a linear programming problem 
        """
        # Create a new problem instance
        self.problem = lp.LpProblem(f"TTS_problem_for_{input_data.school_id}")  # Currently no 'sense'
        self.error_messages = []

        # Formulate the linear programming problem
        self.input_data = input_data
        self.variables = TimetableSolverVariables(inputs=input_data).get_variables()
        constraint_maker = TimetableSolverConstraints(inputs=input_data, variables=self.variables)
        constraint_maker.add_constraints_to_problem(problem=self.problem)

    def solve(self, *args, **kwargs) -> None:
        try:
            self.problem.solve(*args, **kwargs)
        except lp.PulpSolverError as e:
            self.error_messages += [e]
