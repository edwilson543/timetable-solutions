"""Module containing unit tests for the utility functions in timetable_selector app."""

# Django imports
from django.test import TestCase

# Local application imports
from data import models
from timetable_selector.utils import get_summary_stats


class TestViews(TestCase):
    """Test class for function in the utils.py module of timetable_selector views"""
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json", "fixed_classes.json"]

    def test_get_summary_stats_correct(self):
        """
        Test that get summary stats provides the correct values for summarising the (known) contents
        of the test fixtures.
        """
        stats = get_summary_stats(school_access_key=123456)
        # All assertion values are evident from the tests fixtures
        self.assertEqual(stats["total_classes"], 12)
        self.assertEqual(stats["total_lessons"], 100)
        self.assertEqual(stats["total_pupils"], 6)
        self.assertEqual(stats["total_teachers"], 11)
        self.assertIsInstance(stats["busiest_slot"], models.TimetableSlot)
