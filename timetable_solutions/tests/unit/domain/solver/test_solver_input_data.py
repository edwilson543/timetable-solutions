"""Unit tests for the TimetableSolverInputs class"""

# Third party imports
import pytest

# Django imports
from django import test

# Local application imports
from domain.solver.constants import school_dataclasses
from domain.solver import linear_programming as lp


class TestTimetableSolverInputs(test.LiveServerTestCase):
    """
    Note that we use the LiveServerTestCase since the solver is effectively (designed to be possible to be) outside of
    this repository and thus uses the requests module to consume the REST API.
    Therefore we need a full url to pass to requests.get()

    """

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "unsolved_classes.json"]

    # TEST FOR DATA GETTER METHODS
    def test_get_fixed_class_data_valid_url_and_school_access_key(self):
        """Test the solver data loader is able to consume the internal REST API and retrieve FixedClass instances"""
        # Set test parameters
        school_access_key = 123456
        url = f"{self.live_server_url}/api/fixedclasses/?school_access_key={school_access_key}"

        # Execute test unit
        data = lp.TimetableSolverInputs._get_fixed_class_data(url=url)

        # Check the outcome is as expected
        assert isinstance(data, list)  # Since we expect multiple FixedClass instances in a list
        assert len(data) == 24
        for fixed_class in data:
            assert isinstance(fixed_class, school_dataclasses.FixedClass)

    def test_get_fixed_class_invalid_url(self):
        """Test that an invalid API end-point leads to a ValueError when trying to get FixedClass data"""
        url = f"{self.live_server_url}/api/bad-url"
        with pytest.raises(ValueError):
            lp.TimetableSolverInputs._get_fixed_class_data(url=url)

    # TEST FOR DATA GETTER METHODS
    def test_get_unsolved_class_data_valid_url_and_school_access_key(self):
        """Test the solver data loader is able to consume the internal REST API and retrieve UnsolvedClass instances"""
        # Set test parameters
        school_access_key = 123456
        url = f"{self.live_server_url}/api/unsolvedclasses/?school_access_key={school_access_key}"

        # Execute test unit
        data = lp.TimetableSolverInputs._get_unsolved_class_data(url=url)

        # Check the outcome is as expected
        assert isinstance(data, list)  # Since we expect multiple UnsolvedClass instances in a list
        assert len(data) == 12
        for unsolved_class in data:
            assert isinstance(unsolved_class, school_dataclasses.UnsolvedClass)

    def test_get_unsolved_class_invalid_url(self):
        """Test that an invalid API end-point leads to a ValueError when trying to get UnsolvedClass data"""
        url = f"{self.live_server_url}/api/bad-url"
        with pytest.raises(ValueError):
            lp.TimetableSolverInputs._get_unsolved_class_data(url=url)

    def test_get_timetable_slot_data_valid_url_and_school_access_key(self):
        """Test the solver data loader is able to consume the internal REST API and retrieve TimetableSlot instances"""
        # Set test parameters
        school_access_key = 123456
        url = f"{self.live_server_url}/api/timetableslots/?school_access_key={school_access_key}"

        # Execute test unit
        data = lp.TimetableSolverInputs._get_timetable_slot_data(url=url)

        # Check the outcome is as expected
        assert isinstance(data, list)  # Since we expect multiple UnsolvedClass instances in a list
        assert len(data) == 35
        for timetable_slot in data:
            assert isinstance(timetable_slot, school_dataclasses.TimetableSlot)

    def test_get_timetable_slots_invalid_url(self):
        """Test that an invalid API end-point leads to a ValueError when trying to get TimetableSlot data"""
        url = f"{self.live_server_url}/api/bad-url"
        with pytest.raises(ValueError):
            lp.TimetableSolverInputs._get_timetable_slot_data(url=url)
