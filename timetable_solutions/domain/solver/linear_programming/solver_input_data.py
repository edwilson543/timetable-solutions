"""
Module defining how data is accessed by the solver from the API and then stored.
Clearly an API is not necessary here, and instead the TimetableSolverInputs could just call the data layer directly.
The API was implemented for the sake of learning about the Django Rest Framework.
"""

# Standard library imports
import requests
from typing import Dict, List

# Local application imports
from domain.solver.constants.api_endpoints import DataLocation


class TimetableSolverInputs:
    """Class responsible for loading in all schools data (i.e. consuming the API), and then storing this data"""
    def __init__(self, data_location: DataLocation):
        self.data_location = data_location
        self.fixed_class_data = self._get_fixed_class_data(url=data_location.fixed_classes_url)
        self.unsolved_class_data = self._get_unsolved_class_data(url=data_location.unsolved_classes_url)
        self.timetable_slot_data = self._get_timetable_slot_data(url=data_location.timetable_slots_url)

    @staticmethod
    def _get_fixed_class_data(url: str) -> List[Dict]:
        """Method will use the requests library to access data"""
        response = requests.get(url)
        data = response.json()
        return data

    @staticmethod
    def _get_unsolved_class_data(url: str) -> List[Dict]:
        pass

    @staticmethod
    def _get_timetable_slot_data(url: str) -> List[Dict]:
        pass
