"""Module containing unit tests for the utility functions in view_timetables app."""

# Django imports
from django.test import TestCase

# Local application imports
from data import models
from domain.view_timetables.data_pre_processing import get_summary_stats_for_dashboard


class TestViews(TestCase):
    """Test class for function in the data_pre_processing.py module of view_timetables views"""
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json", "fixed_classes.json"]

    def test_get_summary_stats_correct(self):
        """
        Test that get summary stats provides the correct values for summarising the (known) contents
        of the test fixtures.
        """
        stats = get_summary_stats_for_dashboard(school_access_key=123456)
        # All assertion values are evident from the tests fixtures
        self.assertEqual(stats["total_classes"], 12)
        self.assertEqual(stats["total_lessons"], 100)
        self.assertEqual(stats["total_pupils"], 6)
        self.assertEqual(stats["total_teachers"], 11)
        self.assertIsInstance(stats["busiest_slot"], models.TimetableSlot)
