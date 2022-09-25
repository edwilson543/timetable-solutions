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
                "fixed_classes.json"]

    def test_get_fixed_class_data_valid_school_access_key(self):
        """Test that the solver input data loader is able to consume the internal REST API"""
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

    def test_get_fixed_class_invalid_school_access_key(self):
        """Test that an invalid API end-point leads to a ValueError"""
        url = f"{self.live_server_url}/api/bad-url"
        with pytest.raises(ValueError):
            lp.TimetableSolverInputs._get_fixed_class_data(url=url)
