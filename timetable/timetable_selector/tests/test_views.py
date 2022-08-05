"""Module containing unit tests for the views in timetable_selector app."""

# Django imports
from django.test import TestCase
from django.urls import reverse


class TestViews(TestCase):
    """Test class for the timetable_selector views"""
    fixtures = ["classrooms.json", "pupils.json", "teachers.json", "timetable.json", "classes.json"]

    def test_pupil_navigator_response(self):
        response = self.client.get(reverse('pupils_navigator'))
        self.assertIsInstance(response.context["all_pupils"], dict)
