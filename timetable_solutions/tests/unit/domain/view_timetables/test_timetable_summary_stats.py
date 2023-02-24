"""
Module containing unit tests for functions in timetable_summary_stats in the view_timetables app of the domain layer.
"""


# Django imports
from django.core import management
from django.test import TestCase

# Local application imports
from domain.view_timetables import SummaryStats


class TestTimetableSummaryStats(TestCase):
    """
    Test class for the timetable_summary_stats_module, which does include some pre-populated timetable solutions.
    """

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
    ]

    def test_summary_stats_for_dashboard_correct(self):
        """
        Test that the correct summary stats are produced (for the data in the test fixtures).
        """
        # Set test parameters
        management.call_command("loaddata", "lessons_with_solution.json")
        stats = SummaryStats(school_access_key=123456)

        # Execute test unit
        summary = stats.summary_stats

        # Check outcome - see fixtures for info on specific values
        assert summary["has_solutions"]

        assert summary["n_pupils"] == 6
        assert summary["n_teachers"] == 11
        assert summary["n_solved_lessons"] == 12
        assert summary["n_solved_slots"] == 100

        assert summary["daily_solver_lessons"] == {
            "Monday": 20,
            "Tuesday": 20,
            "Wednesday": 20,
            "Thursday": 20,
            "Friday": 20,
        }

        # No user defined lessons in the fixture
        assert summary["daily_user_lessons"] == {}

    def test_summary_stats_unavailable_when_solver_not_run_but_lessons_defined(self):
        """
        Test that 'has_solutions' will be False when the user has uploaded all the required data,
        but not yet run the solver..
        """
        # Set test parameters
        management.call_command("loaddata", "lessons_without_solution.json")
        stats = SummaryStats(school_access_key=123456)

        # Execute test unit
        summary = stats.summary_stats

        # Check outcome - see fixtures for info on specific values
        assert not summary["has_solutions"]

    def test_summary_stats_user_has_not_yet_uploaded_all_data(self):
        """
        Test that 'has_solutions' will be False when no Lesson instances are present in the db.
        """
        # Set test parameters
        stats = SummaryStats(school_access_key=123456)

        # Execute test unit
        summary = stats.summary_stats

        # Check outcome - see fixtures for info on specific values
        assert not summary["has_solutions"]
