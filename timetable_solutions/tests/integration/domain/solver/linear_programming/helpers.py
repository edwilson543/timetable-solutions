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
