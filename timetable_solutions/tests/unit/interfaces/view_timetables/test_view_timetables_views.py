"""
Module containing unit tests for the views in view_timetables app.
"""


# Django imports
from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse

# Local application imports
from interfaces.constants import UrlName


class TestViews(TestCase):
    """
    Test class for the view_timetables app.
    """

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    def test_selection_dashboard_response(self):
        """
        Test that the selection dashboard is being loaded along with the relevant summary stats.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.VIEW_TIMETABLES_DASH.value)

        # Execute test unit
        response = self.client.get(url)

        # Test the keys of the dict are the year groups
        assert response.status_code == 200
        assert response.context["has_solutions"]

    def test_pupil_navigator_response(self):
        """
        Test that the correct full list of pupils indexed by year group is returned by a get request to the
        pupil_navigator view. We test the data structures at successive depths of the nested context dictionary.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.PUPILS_NAVIGATOR.value)

        # Execute test unit
        response = self.client.get(url)

        # Test the keys of the dict are the year groups
        assert response.status_code == 200
        assert "year_groups" in response.context

    def test_teacher_navigator_response(self):
        """Test that the correct full list of teachers is returned, indexed by the first letter of their surname."""
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.TEACHERS_NAVIGATOR.value)

        # Execute test unit
        response = self.client.get(url)
        teachers = response.context["all_teachers"]

        # Test the keys are the relevant alphabet letters
        self.assertEqual(list(teachers.keys()), list("CDFHJMPSTV"))

        # Test the data at an individual key
        self.assertIsInstance(teachers["C"], QuerySet)
        self.assertEqual(len(teachers["C"]), 2)

        # Test the data within the queryset
        fifty = teachers["C"].get(teacher_id=11)
        self.assertEqual(fifty.surname, "Cent")
