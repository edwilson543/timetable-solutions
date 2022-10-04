"""Entry point to the solver"""

# Standard library imports
from typing import List, Optional, Union

# Local application imports
from .solver_input_data import TimetableSolverInputs
from .solver_output_data import TimetableSolverOutcome
from .linear_programming.solver import TimetableSolver


def produce_timetable_solutions(school_access_key: int) -> Union[str, None]:
    """
    Function to be used by the web app to produce the timetable solutions.
    A button is clicked, which corresponds to a view, where that view calls this function.
    :param school_access_key - the unique integer used to access a given school's data via the API
    """
    input_data = TimetableSolverInputs(school_id=school_access_key)
    solver = TimetableSolver(input_data=input_data)
    solver.solve()

    # Assess the outcome and either post the solutions or return why solutions have not been found
    outcome = TimetableSolverOutcome(timetable_solver=solver)
    if outcome.error_messages is None:
        outcome.extract_and_post_results()
    else:
        return outcome.error_messages
