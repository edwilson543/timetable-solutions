"""Unit tests for the TimetableSolverInputs class"""

# Third party imports
import pytest

# Django imports
from django import test

# Local application imports
from domain.solver.constants import school_dataclasses
from domain.solver import linear_programming as lp


class TestTimetableSolverInputsLoading(test.LiveServerTestCase):
    """
    Note that we use the LiveServerTestCase since the solver is effectively (designed to be possible to be) outside of
    this repository and thus uses the requests module to consume the REST API.
    Therefore we need a full url to pass to requests.get()

    This class only tests the data getter methods - meta data extraction is then tested in the class defined below.
    """

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "unsolved_classes.json"]

    # TESTS FOR DATA GETTER METHODS
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


class TestTimetableSolverInputsMetaDataExtraction:
    """TESTS FOR META DATA EXTRACTION METHODS"""

    def test_get_pupil_set(self, fixed_class_data, unsolved_class_data):
        """Test for the get_pupil_set_method on the TimetableSolverInputs class"""
        # Set test parameters
        # noinspection PyTypeChecker
        solver = lp.TimetableSolverInputs(data_location=None)
        solver.fixed_class_data = fixed_class_data
        solver.unsolved_class_data = unsolved_class_data

        # Execute test unit
        pupil_set = solver._get_pupil_set()

        # Check outcome
        assert pupil_set == {1, 2, 3, 4}

    def test_get_teacher_set(self, fixed_class_data, unsolved_class_data):
        """Test for the get_teacher_set_method on the TimetableSolverInputs class"""
        # Set test parameters
        # noinspection PyTypeChecker
        solver = lp.TimetableSolverInputs(data_location=None)
        solver.fixed_class_data = fixed_class_data
        solver.unsolved_class_data = unsolved_class_data

        # Execute test unit
        teacher_set = solver._get_teacher_set()

        # Check outcome
        assert teacher_set == {1, 2}

    def test_get_days_of_weeks_used(self, timetable_slot_data):
        """Test for the get_days_of_weeks_used_set on the TimetableSolverInputs class"""
        # Set test parameters
        # noinspection PyTypeChecker
        solver = lp.TimetableSolverInputs(data_location=None)
        solver.timetable_slot_data = timetable_slot_data

        # Execute test unit
        days_set = solver._get_days_of_weeks_used_set()

        # Check outcome
        assert days_set == {"MONDAY", "TUESDAY"}

