"""Unit tests for the TimetableSolverInputs class"""

# Django imports
from django import test

# Local application imports
from domain.solver import linear_programming as lp


class TestTimetableSolverInputs(test.LiveServerTestCase):
    """
    Note that we use the LiveServerTestCase since the solver is effectively (designed to be possible to be) outside of
    this repository and thus uses the requests module to consume the REST API.
    Therefore we need a full url to pass to requests.get()

    """

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

    def test_get_fixed_class_data(self):
        """Test that the solver input data loader is able to consume the internal REST API"""
        # Set test parameters
        school_access_key = 123456
        url = f"{self.live_server_url}/api/fixedclasses/?school_access_key={school_access_key}"

        # Execute test unit
        data = lp.TimetableSolverInputs._get_fixed_class_data(url=url)

        # Check the outcome is as expected
        assert isinstance(data, list)  # Since we expect multiple FixedClass instances in a list
        assert len(data) == 24
        for fc in data:
            assert fc["school"] == 123456
            assert isinstance(fc["class_id"], str)
            assert isinstance(fc["subject_name"], str)
            assert (isinstance(fc["teacher"], int) or (fc["teacher"] is None))
            assert (isinstance(fc["classroom"], int) or (fc["classroom"] is None))
            assert isinstance(fc["pupils"], list)
            assert isinstance(fc["time_slots"], list)
            assert isinstance(fc["user_defined"], bool)
