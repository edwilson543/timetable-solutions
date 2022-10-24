"""
Module containing unit tests for functions in timetable_summary_stats in the view_timetables app of the domain layer.
"""

# Django imports
from django.test import TestCase

# Local application imports
from domain.view_timetables import get_summary_stats_for_dashboard
from data import models


class TestTimetableSummaryStats(TestCase):
    """Test class for the all functions in the data_pre_processing module of the view_timetables in the domain."""
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

    def test_get_summary_stats_for_dashboard_correct(self):
        """
        Test that the correct summary stats are produced (for the data in the test fixtures).
        """
        # Execute test unit
        stats = get_summary_stats_for_dashboard(school_access_key=123456)

        # Check outcome - see fixtures for info on specific values
        self.assertEqual(stats["total_classes"], 12)
        self.assertEqual(stats["total_lessons"], 100)
        self.assertEqual(stats["total_pupils"], 6)
        self.assertEqual(stats["total_teachers"], 11)

        self.assertEqual(stats["busiest_day"], "Monday")
        self.assertEqual(stats["busiest_day_pct"], 20.0)
        self.assertEqual(stats["quietest_day"], "Monday")
        self.assertEqual(stats["quietest_day_pct"], 20.0)

        self.assertEqual(stats["busiest_time"], "10:00")
        self.assertEqual(stats["busiest_time_pct"], 20.0)
