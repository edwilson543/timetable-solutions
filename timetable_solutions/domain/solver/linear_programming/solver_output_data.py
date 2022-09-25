# Standard library imports
from dataclasses import asdict
import requests
from typing import List

# Local application imports
from domain.solver.constants import school_dataclasses
from domain.solver.linear_programming.solver import TimetableSolver


class TimetableSolverOutcome:
    """
    Class responsible for extracting results from a solved TimetableSolver, and submitting a POST request of these
    back to the main web app
    """

    def __init__(self, timetable_solver: TimetableSolver):
        self.timetable_solver = timetable_solver
        self.solver_fixed_class_data: List[school_dataclasses.FixedClass] | None = None
        self.error_messages = None

    def extract_and_post_results(self) -> None:
        self.solver_fixed_class_data = self._extract_results()
        self._post_results(url=self.timetable_solver.input_data.data_location.fixed_classes_url)
        # TODO - above just sketch of what should happen

    def _extract_results(self) -> List[school_dataclasses.FixedClass]:
        pass

    def _post_results(self, url: str) -> requests.Response:
        """
        Method to post the to-be FixedClass instances created by the solver to the API
        :param url - the API end-point to which we are sending the data
        :return - the status code of the attempted post request
        """
        data_list_of_dicts = [asdict(fixed_class) for fixed_class in self.solver_fixed_class_data]
        response = requests.post(url, json=data_list_of_dicts)
        return response
