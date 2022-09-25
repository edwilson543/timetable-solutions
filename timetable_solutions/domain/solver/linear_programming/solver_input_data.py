"""
Module defining how data is accessed by the solver from the API and then stored.
Clearly an API is not necessary here, and instead the TimetableSolverInputs could just call the data layer directly.
The API was implemented for the sake of learning about the Django Rest Framework.
"""

# Standard library imports
import requests
from typing import List, Set

# Local application imports
from domain.solver.constants.api_endpoints import DataLocation
from domain.solver.constants import school_dataclasses


class TimetableSolverInputs:
    """Class responsible for loading in all schools data (i.e. consuming the API), and then storing this data"""
    def __init__(self, data_location: DataLocation):

        # Store data location
        self.data_location = data_location

        # Submit get requests to timetable solutions ltd. server
        self.fixed_class_data = self._get_fixed_class_data(url=data_location.fixed_classes_url)
        self.unsolved_class_data = self._get_unsolved_class_data(url=data_location.unsolved_classes_url)
        self.timetable_slot_data = self._get_timetable_slot_data(url=data_location.timetable_slots_url)

        # Extract meta data
        self.pupil_set = self._get_pupil_set()

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

    # DATA PRE-PROCESSING METHODS
    def _get_pupil_set(self) -> Set[int]:
        """
        Method to get the exhaustive set of pupil's relevant to the solution.
        :return pupil_set - a set of integers, where each integer represents a pupil
        """
        fixed_class_pupil_set = {pupil for fixed_class in self.fixed_class_data for pupil in fixed_class.pupils}
        unsolved_class_pupil_set = {pupil for usc in self.unsolved_class_data for pupil in usc.pupils}

        pupil_set = fixed_class_pupil_set | unsolved_class_pupil_set
        return pupil_set

    def _get_teacher_list(self) -> List[int]:
        pass

    def _get_days_of_weeks_used(self) -> List[str]:
        pass

    def _get_slots_within_days_used(self) -> List[str]:
        pass
