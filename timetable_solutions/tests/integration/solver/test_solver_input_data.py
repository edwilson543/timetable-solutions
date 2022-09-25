"""Integration test for the TimetableSolverInputs class"""

# Django imports
from django import test

# Local application imports
from domain.solver.constants import school_dataclasses
from domain.solver.constants.api_endpoints import DataLocation
from domain.solver import linear_programming as lp


class TestTimetableSolverInputs(test.LiveServerTestCase):
    """Test that the input loader go load all data, and then extract the metadata"""

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "unsolved_classes.json"]

    def test_timetable_solver_inputs_can_load_in_all_data_and_extract_meta_data(self):
        # Set test parameters
        data_location = DataLocation(school_access_key=123456, protocol_domain=self.live_server_url)

        # Execute the logic
        input_data = lp.TimetableSolverInputs(data_location=data_location)

        # Test the outcome
        # LOADED DATA
        for fc in input_data.fixed_class_data:
            assert isinstance(fc, school_dataclasses.FixedClass)
        for uc in input_data.unsolved_class_data:
            assert isinstance(uc, school_dataclasses.UnsolvedClass)
        for ts in input_data.timetable_slot_data:
            assert isinstance(ts, school_dataclasses.TimetableSlot)

        # META DATA
        assert input_data.pupil_set == {1, 2, 3, 4, 5, 6}