"""Module containing unit tests for data_pre_processing in the view_timetables subdirectory of the domain layer."""

# Django imports
from django.db.models import QuerySet
from django.test import TestCase

# Local application imports
from data import models
from domain import view_timetables


class TestDataPreProcessing(TestCase):
    """Test class for the all functions in the data_pre_processing module of the view_timetables in the domain."""
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

    def test_get_summary_stats_for_dashboard_correct(self):
        """Test that the correct summary stats are produced for the test fixtures."""
        stats = view_timetables.get_summary_stats_for_dashboard(school_access_key=123456)
        # All assertion values are evident from the tests fixtures
        self.assertEqual(stats["total_classes"], 12)
        self.assertEqual(stats["total_lessons"], 100)
        self.assertEqual(stats["total_pupils"], 6)
        self.assertEqual(stats["total_teachers"], 11)
        self.assertIsInstance(stats["busiest_slot"], models.TimetableSlot)

    def test_get_year_indexed_pupils(self):
        """Test that the correct full list of pupils indexed by year group is returned"""
        # Execute the unit of the domain layer
        all_pupils_dict = view_timetables.get_year_indexed_pupils(school_id=123456)

        # Test the correct year group list has been retrieved
        expected_year_groups = list(all_pupils_dict.keys())
        self.assertEqual(expected_year_groups, [models.Pupil.YearGroup.ONE.value, models.Pupil.YearGroup.TWO.value])
        for year_group, pupils in all_pupils_dict.items():
            for pupil in pupils:
                self.assertEqual(pupil["year_group"], year_group)  # Check the pupils have been correctly assigned

        # Test that each key corresponds to a value, which is the query set of pupils in that year group
        year_one = all_pupils_dict[models.Pupil.YearGroup.ONE.value]
        self.assertIsInstance(year_one, QuerySet)
        self.assertEqual(len(year_one), 3)

        # Test an individual pupil returned from the query set
        john_smith = year_one.get(pupil_id=1)
        self.assertIsInstance(john_smith, dict)
        self.assertEqual(john_smith["firstname"], "John")

    def test_get_letter_indexed_teachers(self):
        """Test that the correct full list of teachers, indexed by their surname letters is returned"""
        all_teachers_dict = view_timetables.get_letter_indexed_teachers(school_id=123456)

        # Test the keys are the relevant alphabet letters
        self.assertEqual(list(all_teachers_dict.keys()), list("CDFHJMPSTV"))
        for letter, teachers in all_teachers_dict.items():
            for teacher in teachers:
                self.assertEqual(teacher["surname"][0], letter)  # Check the surnames' first letters match the index

        # Test the data at an individual key
        self.assertIsInstance(all_teachers_dict["C"], QuerySet)
        self.assertEqual(len(all_teachers_dict["C"]), 2)

        # Test the data within the queryset
        fifty = all_teachers_dict["C"].get(teacher_id=11)
        self.assertEqual(fifty["surname"], "Cent")
