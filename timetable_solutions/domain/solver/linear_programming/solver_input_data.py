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
    def _get_fixed_class_data(url: str) -> List[school_dataclasses.FixedClass] | None:
        """
        Method retrieving data on (user-defined) FixedClass instances from the API and converting them into the
        dataclass structure used by the solver.
        :param url - the API endpoint (on a live server) where FixedClass data for the relevant school is available
        :return - data -  a list of dataclass instances, with one dataclass per FixedClass
        """
        response = requests.get(url)
        if response.status_code == 200:
            data_list = response.json()
            data = [school_dataclasses.FixedClass(**instance) for instance in data_list]
            return data
        elif response.status_code == 204:
            # This does not represent an error since users do not have to define any FixedClass instances
            return None
        else:
            raise ValueError(f"Specified url not a valid API end point: {url}")

    # DATA GETTER METHODS - API CONSUMERS
    @staticmethod
    def _get_unsolved_class_data(url: str) -> List[school_dataclasses.UnsolvedClass]:
        """
        Method retrieving data on UnsovledClass instances from the API and converting them into the
        dataclass structure used by the solver. UnsolvedClasses are what the solver must solve...
        :param url - the API endpoint (on a live server) where UnsolvedClass data for the relevant school is available
        :return - data - a list of dataclass instances, with one dataclass per FixedClass
        """
        response = requests.get(url)
        if response.status_code == 200:
            data_list = response.json()
            data = [school_dataclasses.UnsolvedClass(**instance) for instance in data_list]
            return data
        elif response.status_code == 204:
            raise ValueError(f"Specified url did not contain any relevant UnsolvedClass instances, and thus"
                             f" the solver is not able to formulate the problem {url}")
        else:
            raise ValueError(f"Specified url not a valid API end point: {url}")

    @staticmethod
    def _get_timetable_slot_data(url: str) -> List[school_dataclasses.TimetableSlot]:
        """
        Method retrieving data on TimetableSlot instances from the API and converting them into the
        dataclass structure used by the solver. The solver must understand which TimetableSlots are available in the
        solution
        :param url - the API endpoint (on a live server) where UnsolvedClass data for the relevant school is available
        :return - data - a list of dataclass instances, with one dataclass per FixedClass
        """
        response = requests.get(url)
        if response.status_code == 200:
            data_list = response.json()
            data = [school_dataclasses.TimetableSlot(**instance) for instance in data_list]
            return data
        elif response.status_code == 204:
            raise ValueError(f"Specified url did not contain any relevant TimetableSlot instances, and thus"
                             f" the solver is not able to formulate the problem {url}")
        else:
            raise ValueError(f"Specified url not a valid API end point: {url}")

    # DATA PRE PROCESSING
    def _get_pupil_list_and_check_consistent(self) -> List[int]:
        pass

    def _get_teacher_list_and_check_consistent(self) -> List[int]:
        pass

    def _get_days_of_weeks_used(self) -> List[str]:
        pass

    def _get_slots_within_days_used(self) -> List[str]:
        pass
