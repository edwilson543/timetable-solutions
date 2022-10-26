"""Module containing unit tests for the views in view_timetables app."""

# Local application imports
from datetime import time

# Django imports
from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse

# Local application imports
from constants.url_names import UrlName
from data import models
from domain.view_timetables.timetable_colours import TimetableColour


class TestViews(TestCase):
    """Test class for the view_timetables views"""
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "fixed_classes_lunch.json"]

    def test_pupil_navigator_response(self):
        """
        Test that the correct full list of pupils indexed by year group is returned by a get request to the
        pupil_navigator view. We test the data structures at successive depths of the nested context dictionary.
        """
        # Set test parameters
        self.client.login(username='dummy_teacher', password='dt123dt123')
        url = reverse(UrlName.PUPILS_NAVIGATOR.value)

        # Execute test unit
        response = self.client.get(url)

        # Test the keys of the dict are the year groups
        all_pupils_dict = response.context["all_pupils"]
        year_groups_list = list(all_pupils_dict.keys())
        self.assertEqual(year_groups_list, [models.Pupil.YearGroup.ONE.value, models.Pupil.YearGroup.TWO.value])

        # Test that each key corresponds to a value, which is the query set of pupils in that year group
        year_one = all_pupils_dict[models.Pupil.YearGroup.ONE.value]
        self.assertIsInstance(year_one, QuerySet)
        self.assertEqual(len(year_one), 3)

        # Test an individual pupil returned from the query set
        john_smith = year_one.get(pupil_id=1)
        self.assertIsInstance(john_smith, dict)
        self.assertEqual(john_smith["firstname"], "John")

    def test_teacher_navigator_response(self):
        """Test that the correct full list of teachers is returned, indexed by the first letter of their surname."""
        # Set test parameters
        self.client.login(username='dummy_teacher', password='dt123dt123')
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
        self.assertEqual(fifty["surname"], "Cent")

    def test_pupil_timetable_view_response_correct_timetable(self):
        """
        Test that the correct context is returned by a get request to the pupil_timetable_view for pupil 1.
        Note there are three elements within the context of the HTTP response - each of which is tested in turn, one of
        which is the pupil's timetable.
        """
        # Set test parameters
        self.client.login(username='dummy_teacher', password='dt123dt123')
        url = reverse(UrlName.PUPIL_TIMETABLE.value, kwargs={"id": 1})

        # Execute test unit
        response = self.client.get(url)

        # Test pupil context
        pupil = response.context["pupil"]
        self.assertIsInstance(pupil, models.Pupil)
        self.assertEqual(pupil.firstname, "John")
        self.assertEqual(pupil.year_group, 1)

        # Test timetable context
        timetable = response.context["timetable"]
        monday_period_one = timetable[time(hour=9)][models.WeekDay.MONDAY.label]
        self.assertIsInstance(monday_period_one, models.FixedClass)
        self.assertEqual(monday_period_one.subject_name, "MATHS")
        self.assertEqual(monday_period_one.classroom.building, "MB")
        free_period = timetable[time(hour=12)][models.WeekDay.THURSDAY.label]
        # For free periods, the dictionary value is a string as opposed to a FixedClass instance
        self.assertEqual(free_period, "FREE")

        # Test colours context
        colours = response.context["class_colours"]
        self.assertIsInstance(colours, dict)
        self.assertEqual(colours["MATHS"],
                         TimetableColour.COLOUR_RANKING.value[1])  # [1] since maths' rank is 1 on pupil's timetable
        self.assertEqual(colours[TimetableColour.FREE.name], TimetableColour.FREE.value)

    def test_teacher_timetable_view_correct_response(self):
        """
        Unit test that the context returned by a GET request to the teacher_timetable_view function, containing the
        relevant timetable etc.
        """
        # Set test parameters
        self.client.login(username='dummy_teacher', password='dt123dt123')
        url = reverse(UrlName.TEACHER_TIMETABLE.value, kwargs={"id": 6})  # Timetable for Greg Thebaker

        # Execute test unit
        response = self.client.get(url)

        # Test teacher context
        teacher = response.context["teacher"]
        self.assertIsInstance(teacher, models.Teacher)
        self.assertEqual(teacher.firstname, "Greg")

        # Test timetable content
        timetable = response.context["timetable"]
        monday_period_one = timetable[time(hour=9)][models.WeekDay.MONDAY.label]
        self.assertIsInstance(monday_period_one, models.FixedClass)
        self.assertEqual(monday_period_one.subject_name, "FRENCH")
        free_period = timetable[time(hour=10)][models.WeekDay.MONDAY.label]
        self.assertEqual(free_period, "FREE")

        # Test the colours context
        colours = response.context["year_group_colours"]
        self.assertIsInstance(colours, dict)
        self.assertEqual(colours[models.Pupil.YearGroup.ONE.value], TimetableColour.COLOUR_RANKING.value[1])
        self.assertEqual(colours[TimetableColour.FREE.name], TimetableColour.FREE.value)
        self.assertEqual(colours[TimetableColour.LUNCH.name], TimetableColour.LUNCH.value)
