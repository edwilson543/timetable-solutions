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
from domain.solver.constants import school_dataclasses


class TimetableSolverInputs:
    """Class responsible for loading in all schools data (i.e. consuming the API), and then storing this data"""
    def __init__(self, data_location: DataLocation):
        self.data_location = data_location
        self.fixed_class_data = self._get_fixed_class_data(url=data_location.fixed_classes_url)
        self.unsolved_class_data = self._get_unsolved_class_data(url=data_location.unsolved_classes_url)
        self.timetable_slot_data = self._get_timetable_slot_data(url=data_location.timetable_slots_url)

    @staticmethod
    def _get_fixed_class_data(url: str) -> List[school_dataclasses.FixedClass]:
        """
        Method retrieving data on (user-defined) FixedClass instances from the API and converting them into the
        dataclass structure used by the solver.
        :param url - the API endpoint (on a live server) where FixedClass data for the relevant school is available
        :return - data
        """
        response = requests.get(url)
        if response.status_code == 200:
            data_list = response.json()
            data = [school_dataclasses.FixedClass(**instance) for instance in data_list]
            return data
        elif response.status_code == 204:
            # This does not represent an error since users do not have to define any FixedClass instances
            return []
        else:
            raise ValueError(f"Specified url not a valid API end point: {url}")

    # DATA IMPORT
    @staticmethod
    def _get_unsolved_class_data(url: str) -> List[Dict]:
        pass

    @staticmethod
    def _get_timetable_slot_data(url: str) -> List[Dict]:
        pass

    # DATA PRE PROCESSING
    def _get_pupil_list_and_check_consistent(self) -> List[int]:
        pass

    def _get_teacher_list_and_check_consistent(self) -> List[int]:
        pass

    def _get_days_of_weeks_used(self) -> List[str]:
        pass

    def _get_slots_within_days_used(self) -> List[str]:
        pass
