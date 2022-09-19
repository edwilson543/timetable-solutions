"""Tests for the ModelViewSet classes"""

# Standard library imports
import json

# Third party imports
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response

# Django imports
from django import test

# Local application imports
from base_files.settings import BASE_DIR
from data import models
from interfaces.api_to_solver import views


class TestFixedClassViewSet(test.TestCase):
    """Tests for the FixedClass ModelViewSet"""
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]
    fixture_location = BASE_DIR / "data" / "fixtures"

    # GET REQUESTS
    @staticmethod
    def submit_get_request_for_fixed_classes(school_access_key: int) -> Response:
        """Method to submit a get request for a given school access key's FixedClass data, and return the response"""
        url = f"/fixedclasses/?school_access_key={school_access_key}"  # URL with school access key query
        request_factory = APIRequestFactory()
        view = views.FixedClassViewSet.as_view({"get": "list"})

        # Submit a GET to API request
        request = request_factory.get(url)
        response = view(request)
        return response

    def test_correct_data_returned_for_get_request_with_valid_school_access_key(self):
        """Test that the full set of serialised fixed classes in the fixture is returned"""
        response = self.submit_get_request_for_fixed_classes(school_access_key=123456)

        actual_data_unordered = [dict(ordered_dict) for ordered_dict in response.data]
        with open((self.fixture_location / "fixed_classes.json")) as used_fixture:
            fixture_json_data = json.load(used_fixture)
        expected_data = [item["fields"] for item in fixture_json_data]
        self.assertEqual(actual_data_unordered, expected_data)

    def test_no_data_returned_for_get_request_with_invalid_school_access_key(self):
        """Test that an empty json list is returned for a get request specifying an invalid school access key"""

        response = self.submit_get_request_for_fixed_classes(school_access_key=12345)
        self.assertEqual(response.data, [])
        # TODO add test for status code 204 once implemented

    # POST REQUESTS
    # TODO - make work
    # def test_post_request_for_valid_fixed_class_instance(self):
    #     """Method to test that we can post a valid instance of the FixedClass model via the API"""
    #     # Set test parameters
    #     fixed_class_1 = {
    #         "school": 123456, "class_id": "TEST_1", "subject_name": "MATHS", "teacher": 1,
    #         "classroom": 1, "pupils": [1, 2], "time_slots": [1, 2], "user_defined": False
    #     }
    #     fixed_class_2 = {
    #         "school": 123456, "class_id": "TEST_2", "subject_name": "MATHS", "teacher": 1,
    #         "classroom": 1, "pupils": [1, 2], "time_slots": [3, 4], "user_defined": False
    #     }
    #     fixed_classes = [fixed_class_1, fixed_class_2]
    #
    #     # Submit the POST request to API
    #     request_factory = APIRequestFactory()
    #     request = request_factory.post("/fixedclasses/", fixed_classes, format="json")
    #     view = views.FixedClassViewSet.as_view({"post": "list"})
    #     response = view(request)
    #
    #     # Test the outcome to the database
    #     fc = models.FixedClass.objects.get_all_school_fixed_classes(school_id=123456)
    #     self.assertEqual(fc.count(), 26)
