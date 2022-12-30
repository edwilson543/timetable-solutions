"""
Module containing unit tests for functions in timetable_summary_stats in the view_timetables app of the domain layer.
"""

# Django imports
from django.test import TestCase

# Local application imports
from domain.view_timetables import get_summary_stats_for_dashboard


class TestTimetableSummaryStats(TestCase):
    """
    Test class for the timetable_summary_stats_module, which does include some pre-populated timetable solutions.
    """

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "pupils.json",
        "teachers.json",
        "timetable.json",
        "lessons_with_solution",
    ]  # Final fixture contains the timetable solutions to be summarised

    def test_get_summary_stats_for_dashboard_correct(self):
        """
        Test that the correct summary stats are produced (for the data in the test fixtures).
        """
        # Execute test unit
        stats = get_summary_stats_for_dashboard(school_access_key=123456)

        # Check outcome - see fixtures for info on specific values
        self.assertEqual(stats["total_classes"], 24)
        self.assertEqual(stats["total_lessons"], 100)
        self.assertEqual(stats["total_pupils"], 6)
        self.assertEqual(stats["total_teachers"], 11)

        self.assertEqual(
            stats["busiest_days"],
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        )
        self.assertEqual(stats["busiest_days_pct"], 20.0)
        self.assertEqual(
            stats["quietest_days"],
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        )
        self.assertEqual(stats["quietest_days_pct"], 20.0)

        self.assertEqual(stats["busiest_times"], ["10:00"])
        self.assertEqual(stats["busiest_times_pct"], 20.0)


class TestTimetableSummaryStatsNoTimetablesLoaded(TestCase):
    """
    Test class for the timetable_summary_stats_module, which does NOT include some pre-populated timetable solutions.
    """

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "pupils.json",
        "teachers.json",
        "timetable.json",
    ]

    def test_get_summary_stats_for_dashboard_no_timetable_solutions(self):
        """
        Test that a singleton dictionary is returned when the user does not have any timetable solutions to view.
        """
        # Set test parameters
        expected_dict = {"has_solutions": False}

        # Execute test unit
        stats = get_summary_stats_for_dashboard(school_access_key=123456)

        # Check outcome
        self.assertEqual(stats, expected_dict)
