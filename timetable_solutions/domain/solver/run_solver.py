"""Entry point to the solver"""

# Standard library imports
from typing import List, Optional, Union

# Local application imports
from domain.solver.constants.api_endpoints import DataLocation
import linear_programming


def produce_timetable_solutions(school_access_key: int,
                                protocol_domain: Optional[str] = None) -> Union[None, List[str]]:
    """
    Function to be used by the web app to produce the timetable solutions.
    A button is clicked, which corresponds to a view, where that view calls this function.
    :param school_access_key - the unique integer used to access a given school's data via the API
    :param protocol_domain - the protocol and domain name of the main web application using this solver
    """
    # Locate the API endpoints for the necessary data
    if protocol_domain is None:
        data_location = DataLocation(school_access_key=school_access_key)
    else:
        data_location = DataLocation(school_access_key=school_access_key, protocol_domain=protocol_domain)
    input_data = linear_programming.TimetableSolverInputs(data_location=data_location)
    input_data.get_and_set_all_data()

    # Formulate the linear programming problem and try to solve
    variable_maker = linear_programming.TimetableSolverVariables(inputs=input_data)
    variables = variable_maker.get_variables()
    solver = linear_programming.TimetableSolver(input_data=input_data)

    # Assess the outcome and either post the solutions or return why solutions have not been found
    outcome = linear_programming.TimetableSolverOutcome(timetable_solver=solver)
    if outcome.error_messages is None:
        outcome.extract_and_post_results()
    else:
        return outcome.error_messages
