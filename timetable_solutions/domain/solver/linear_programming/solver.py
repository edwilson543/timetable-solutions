# Standard library imports
from typing import Any

# Third party imports
import pulp as lp

# Local application imports
from domain.solver.solver_input_data import TimetableSolverInputs
from domain.solver.linear_programming.solver_constraints import (
    TimetableSolverConstraints,
)
from domain.solver.linear_programming.solver_objective import TimetableSolverObjective
from domain.solver.linear_programming.solver_variables import TimetableSolverVariables


class TimetableSolver:
    """
    Class to formulate and solve the timetable scheduling problem as a linear programming problem.
    Subclass of the pulp LpProblem class to allow use of solve method
    """

    def __init__(self, input_data: TimetableSolverInputs):
        """
        :param - input_data - passing this to __init__ triggers the formulation of the timetable solution problem as
        a linear programming problem
        """
        # Create a new problem instance - maximise since objective components are formulated such that bigger is better
        self.problem = lp.LpProblem(
            f"TTS_problem_for_{input_data.school_id}", sense=lp.LpMaximize
        )
        self.error_messages: list[str] = []

        # Formulate the linear programming problem
        self.input_data = input_data
        if len(self.input_data.error_messages) > 0:
            raise ValueError(
                "TimetableSolver was passed input data containing errors!\n"
                f"{self.input_data.error_messages}"
            )
        self.variables = TimetableSolverVariables(inputs=input_data)

        constraint_maker = TimetableSolverConstraints(
            inputs=input_data, variables=self.variables
        )
        constraint_maker.add_constraints_to_problem(problem=self.problem)

        objective_maker = TimetableSolverObjective(
            inputs=input_data, variables=self.variables
        )
        objective_maker.add_objective_to_problem(problem=self.problem)

    def solve(self, *args: Any, **kwargs: Any) -> None:
        """
        Method calling the default PuLP solver (COIN API), and recording the error message if unsuccessful.
        """
        try:
            self.problem.solve(*args, **kwargs)
        except lp.PulpSolverError as e:
            self.error_messages += [e]
