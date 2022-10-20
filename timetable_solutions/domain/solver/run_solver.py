"""
Entry point to the solver, both in terms of using it, and in terms of the interfaces layer.
The function below and SolutionSpecification are the only two objects used outside of domain/solver
"""

# Standard library imports
from typing import List

# Local application imports
from data import models
from .solver_input_data import TimetableSolverInputs, SolutionSpecification
from .solver_output_data import TimetableSolverOutcome
from .linear_programming.solver import TimetableSolver


def produce_timetable_solutions(school_access_key: int, solution_specification: SolutionSpecification,
                                clear_existing: bool = True) -> List[str]:
    """
    Function to be used by the web app to produce the timetable solutions.
    A button is clicked, creates a POST request handled by the CreateTimetable view which then calls this function,
    providing the solution spec via a form.

    :param school_access_key - the unique integer used to access a given school's data.
    :param solution_specification - the user-defined requirements for how the solution should be generated.
    :param clear_existing - whether or not to produce any existing solutions found by the solver.
    :return The list of error messages encountered at the earliest point of the process.
    """
    if clear_existing:
        models.FixedClass.delete_all_non_user_defined_fixed_classes(school_id=school_access_key)

    input_data = TimetableSolverInputs(school_id=school_access_key, solution_specification=solution_specification)
    if len(input_data.error_messages) > 0:
        return input_data.error_messages

    solver = TimetableSolver(input_data=input_data)
    solver.solve()
    # Assess the outcome and either post the solutions or return why solutions have not been found
    outcome = TimetableSolverOutcome(timetable_solver=solver)
    return outcome.error_messages
