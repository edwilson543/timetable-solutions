"""
Module containing unit tests for data_pre_processing in the view_timetables subdirectory of the domain layer.
"""

# Third party imports
import pandas as pd

# Django imports
from django.db.models import QuerySet
from django.test import TestCase

# Local application imports
from data import constants
from data import models
from domain import view_timetables


class TestTimetableConstruction(TestCase):
    """
    Test class for the all functions in the timetable_constructor module of the view_timetables in the domain.
    """

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "teachers.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    # PUPIL / TEACHER NAVIGATOR PREPROCESSING TESTS
    def test_get_pupil_year_groups(self):
        """Test that the correct queryset of year groups (and associated) pupils is returned"""
        # Execute the unit of the domain layer
        all_ygs = view_timetables.get_pupil_year_groups(school_id=123456)

        # Test the correct year group list has been retrieved,
        # in particular that "Reception", which has no pupils, is not included.
        expected_year_groups = ["1", "2"]
        actual_year_groups = list(all_ygs.values_list("year_group", flat=True))
        assert expected_year_groups == actual_year_groups

        for year_group in all_ygs:
            pupils = year_group.pupils.all()
            assert isinstance(pupils, models.PupilQuerySet)
            assert pupils.count() == 3

        assert all_ygs.first().pupils.first().firstname == "Lynn"

    def test_get_letter_indexed_teachers(self):
        """Test that the correct full list of teachers, indexed by their surname letters is returned"""
        all_teachers_dict = view_timetables.get_letter_indexed_teachers(
            school_id=123456
        )

        # Test the keys are the relevant alphabet letters
        self.assertEqual(list(all_teachers_dict.keys()), list("CDFHJMPSTV"))
        for letter, teachers in all_teachers_dict.items():
            for teacher in teachers:
                self.assertEqual(
                    teacher["surname"][0], letter
                )  # Check the surnames' first letters match the index

        # Test the data at an individual key
        self.assertIsInstance(all_teachers_dict["C"], QuerySet)
        self.assertEqual(len(all_teachers_dict["C"]), 2)

        # Test the data within the queryset
        fifty = all_teachers_dict["C"].get(teacher_id=11)
        self.assertEqual(fifty["surname"], "Cent")

    # PUPIL / TEACHER TIMETABLE PREPROCESSING TESTS
    def test_get_timetable_slot_indexed_timetable_for_a_pupil(self):
        """Test that the correct timetable is returned for a given pupil, in the correct structure."""
        # Data setup
        pupil = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)
        lessons = pupil.lessons.all()
        timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )

        # Run the relevant domain unit
        timetable = (
            view_timetables.timetable_constructor.get_timetable_slot_indexed_timetable(
                lessons=lessons, timetable_slots=timetable_slots
            )
        )

        # Test assertions
        monday_period_one = timetable["09:00-10:00"][constants.Day.MONDAY.label]
        self.assertIsInstance(monday_period_one, models.Lesson)
        self.assertEqual(monday_period_one.subject_name, "MATHS")
        self.assertEqual(monday_period_one.classroom.building, "MB")
        free_period = timetable["12:00-13:00"][constants.Day.THURSDAY.label]
        # For free periods, the dictionary value is a string as opposed to a Lesson instance
        self.assertEqual(
            free_period, view_timetables.TimetableColourAssigner.Colour.FREE.name
        )

    def test_get_timetable_slot_indexed_timetable_for_a_teacher(self):
        """Test that the correct timetable is returned for a given pupil, in the correct structure."""
        # Data setup
        teacher = models.Teacher.objects.get_individual_teacher(
            school_id=123456, teacher_id=6
        )
        lessons = teacher.lessons.all()
        timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )

        # Run the relevant domain unit
        timetable = (
            view_timetables.timetable_constructor.get_timetable_slot_indexed_timetable(
                lessons=lessons, timetable_slots=timetable_slots
            )
        )

        # Test assertions
        monday_period_one = timetable["09:00-10:00"][constants.Day.MONDAY.label]
        self.assertIsInstance(monday_period_one, models.Lesson)
        self.assertEqual(monday_period_one.subject_name, "FRENCH")
        free_period = timetable["10:00-11:00"][constants.Day.MONDAY.label]
        self.assertEqual(
            free_period, view_timetables.TimetableColourAssigner.Colour.FREE.name
        )

    # TESTS FOR CSV FILES
    def test_get_pupil_timetable_as_csv(self):
        """
        Test that pupil timetables are correctly processed into csv file buffers.
        """
        # Set test parameters
        school_id = 123456
        pupil_id = 1

        # Execute test unit
        _, csv_buffer = view_timetables.get_pupil_timetable_as_csv(
            school_id=school_id, pupil_id=pupil_id
        )

        # Check outcome - basic structure
        timetable = pd.read_csv(csv_buffer, index_col="Time")

        self.assertEqual(timetable.isnull().sum().sum(), 0)
        self.assertEqual(
            list(timetable.columns),
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        )
        self.assertEqual(timetable.index.name, "Time")

        # Check random specific element
        thursday_two_pm = timetable.loc["14:00-15:00", "Thursday"]
        self.assertEqual(thursday_two_pm, "Maths")

    def test_get_teacher_timetable_as_csv(self):
        """
        Test that teacher timetables are correctly processed into csv file buffers.
        """
        # Set test parameters
        school_id = 123456
        teacher_id = 1

        # Execute test unit
        _, csv_buffer = view_timetables.get_teacher_timetable_as_csv(
            school_id=school_id, teacher_id=teacher_id
        )

        # Check outcome - basic structure
        timetable = pd.read_csv(csv_buffer, index_col="Time")

        self.assertEqual(timetable.isnull().sum().sum(), 0)
        self.assertEqual(
            list(timetable.columns),
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        )
        self.assertEqual(timetable.index.name, "Time")

        # Check random specific element
        tuesday_ten_am = timetable.loc["10:00-11:00", "Tuesday"]
        self.assertEqual(tuesday_ten_am, "French")
