"""Entry point to the solver"""

# Standard library imports
from typing import List

# Local application imports
from domain.solver.constants.api_endpoints import DataLocation
from domain.solver.linear_programming.solver_input_data import TimetableSolverInputs
from domain.solver.linear_programming.solver import TimetableSolver
from domain.solver.linear_programming.solver_output_data import TimetableSolverOutcome


def produce_timetable_solutions(school_access_key: int, domain_name: str | None = None) -> None | List[str]:
    """
    Function to be used by the web app to produce the timetable solutions.
    A button is clicked, which corresponds to a view, where that view calls this function.
    :param school_access_key - the unique integer used to access a given school's data via the API
    :param domain_name - the domain name of the main web application using this solver
    """
    # Locate the API endpoints for the necessary data
    if domain_name is None:
        data_location = DataLocation(school_access_key=school_access_key)
    else:
        data_location = DataLocation(school_access_key=school_access_key, domain_name=domain_name)
    input_data = TimetableSolverInputs(data_location=data_location)

    # Formulate the linear programming problem and try to solve
    solver = TimetableSolver(input_data=input_data)

    # Assess the outcome and either post the solutions or return why solutions have not been found
    outcome = TimetableSolverOutcome(timetable_solver=solver)
    if outcome.error_messages is None:
        outcome.post_results()
    else:
        return outcome.error_messages
