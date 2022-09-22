# Standard library imports
from typing import Dict, List

# Local application imports
from domain.solver.linear_programming.solver import TimetableSolver


class TimetableSolverOutcome:
    """
    Class responsible for extracting results from a solved TimetableSolver, and submitting a POST request of these
    back to the main web app
    """
    def __init__(self, timetable_solver: TimetableSolver):
        self.timetable_solver = timetable_solver
        self.solver_fixed_class_data = self._extract_results()
        self.error_messages = None

    def _extract_results(self) -> List[Dict]:
        pass

    def post_results(self) -> None:
        pass
