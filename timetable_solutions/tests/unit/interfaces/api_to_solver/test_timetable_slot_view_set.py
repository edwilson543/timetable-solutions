"""Tests for the UnsolvedClass ModelViewSet, which only allows GET requests."""

# Standard library imports
import json

# Django imports
from django import test

# Local application imports
from base_files.settings import BASE_DIR


class TestTimetableSlotViewSet(test.TestCase):
    """Tests for the TimetableSlot ModelViewSet"""
    fixtures = ["user_school_profile.json", "timetable.json"]
    fixture_location = BASE_DIR / "data" / "fixtures"

    # GET REQUESTS
    def test_correct_data_returned_for_get_request_with_valid_school_access_key(self):
        """Test that the full set of serialised fixed classes in the fixture is returned"""
        # Set test parameters
        school_access_key = 123456
        url = f"/api/timetableslots/?school_access_key={school_access_key}"  # URL with school access key query

        # Submit the GET request
        response = self.client.get(url)

        # Test the outcome is the same as the fixture (which only contains data for that school)
        self.assertEqual(response.status_code, 200)

        actual_data_unordered = [dict(ordered_dict) for ordered_dict in response.data]
        with open((self.fixture_location / "timetable.json")) as used_fixture:
            fixture_json_data = json.load(used_fixture)
        expected_data = [item["fields"] for item in fixture_json_data]

        for item in expected_data:
            item.pop("school")  # Since school does not get serialised with the UnsolvedClasses
            self.assertIn(item, actual_data_unordered)

    def test_no_data_returned_for_get_request_with_invalid_school_access_key(self):
        """Test that an empty json list is returned for a get request specifying an invalid school access key"""
        # Set test parameters
        school_access_key = 111111  # Note no data for this school access key
        url = f"/api/timetableslots/?school_access_key={school_access_key}"  # URL with school access key query

        # Submit the GET request
        response = self.client.get(url)

        # Test the outcome
        self.assertEqual(response.status_code, 204)  # No content relevant to request
        self.assertEqual(response.data, [])
