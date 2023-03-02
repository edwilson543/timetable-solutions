"""Helper functions for linear programming tests."""


# Local application imports
from data import models
from domain import solver
from tests import domain_factories


def get_solution(
    school: models.School, spec: solver.SolutionSpecification | None = None
) -> solver.TimetableSolver:
    """Instantiate, solve and return a TimetableSolver for a school."""
    if spec is None:
        spec = domain_factories.SolutionSpecification()
    data = solver.TimetableSolverInputs(
        school_id=school.school_access_key, solution_specification=spec
    )
    solver_ = solver.TimetableSolver(input_data=data)
    solver_.solve()
    return solver_


def lesson_occurs_at_slot(
    variables: solver.TimetableSolverVariables,
    lesson: models.Lesson,
    slot: models.TimetableSlot,
) -> bool:
    """
    Determine whether a solved set of decision variable implies that a lesson
    will take place at a certain slot.
    """
    dec_vars = variables.decision_variables
    var_key = solver.var_key(lesson_id=lesson.lesson_id, slot_id=slot.slot_id)
    return bool(dec_vars[var_key].varValue)
