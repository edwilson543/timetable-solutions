# Standard library imports

# Local application imports
from domain.solver.linear_programming.solver import TimetableSolver


class TimetableSolverOutcome:
    """
    Class responsible for extracting results from a solved TimetableSolver, and submitting a POST request of these
    back to the main web app
    """

    def __init__(self, timetable_solver: TimetableSolver):
        self._timetable_solver = timetable_solver
        self._input_data = timetable_solver.input_data
        self._variables = timetable_solver.variables
        self.error_messages = None

    def extract_and_post_results(self) -> None:
        fixed_classes = self._extract_results()
        self._save_results_to_db(fixed_classes=fixed_classes)
        # TODO - above just sketch of what should happen

    def _extract_results(self):
        pass

    def _save_results_to_db(self, fixed_classes) -> None:
        pass
