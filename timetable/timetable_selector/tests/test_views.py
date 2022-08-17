"""Module containing unit tests for the views in timetable_selector app."""

# Django imports
from django.db.models import QuerySet
from django.test import Client, TestCase
from django.urls import reverse

# Local application imports
from ..models import Pupil, TimetableSlot, FixedClass, Teacher


class TestViews(TestCase):
    """Test class for the timetable_selector views"""
    fixtures = ["users.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json", "classes.json"]

    def test_pupil_navigator_response(self):
        """
        Test that the correct full list of pupils indexed by year group is returned by a get request to the
        pupil_navigator view. We test the data structures at successive depths of the nested context dictionary.
        """
        self.client.login(username='dummy_teacher', password='dt123dt123')
        url = reverse('pupils_navigator')
        response = self.client.get(url)

        # Test the keys of the dict are the year groups
        all_pupils_dict = response.context["all_pupils"]
        year_groups_list = list(all_pupils_dict.keys())
        self.assertEqual(year_groups_list, [Pupil.YearGroup.ONE.value, Pupil.YearGroup.TWO.value])

        # Test that each key corresponds to a value, which is the query set of pupils in that year group
        year_one = all_pupils_dict[Pupil.YearGroup.ONE.value]
        self.assertIsInstance(year_one, QuerySet)
        self.assertEqual(len(year_one), 3)

        # Test an individual pupil returned from the query set
        john_smith = year_one.get(pupil_id=1)
        self.assertIsInstance(john_smith, dict)
        self.assertEqual(john_smith["firstname"], "John")

    def test_teacher_navigator_response(self):
        """Test that the correct full list of teachers is returned, indexed by the first letter of their surname."""
        self.client.login(username='dummy_teacher', password='dt123dt123')
        url = reverse('teachers_navigator')
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
        self.client.login(username='dummy_teacher', password='dt123dt123')
        url = reverse('pupil_timetable_view', kwargs={"pupil_id": 1})
        response = self.client.get(url)

        # Test pupil context
        pupil = response.context["pupil"]
        self.assertIsInstance(pupil, Pupil)
        self.assertEqual(pupil.firstname, "John")
        self.assertEqual(pupil.year_group, 1)

        # Test timetable context
        timetable = response.context["timetable"]
        monday_period_one = timetable[TimetableSlot.PeriodStart.PERIOD_ONE.value][TimetableSlot.WeekDay.MONDAY.value]
        self.assertIsInstance(monday_period_one, FixedClass)
        self.assertEqual(monday_period_one.subject_name, FixedClass.SubjectColour.MATHS.name)
        self.assertEqual(monday_period_one.classroom.building, "MB")
        free_period = timetable[TimetableSlot.PeriodStart.PERIOD_FOUR.value][TimetableSlot.WeekDay.THURSDAY.value]
        self.assertEqual(free_period, FixedClass.SubjectColour.FREE.name)  # string returned, not a FixedClass instance

        # Test colours context
        colours = response.context["class_colours"]
        self.assertIsInstance(colours, dict)
        self.assertEqual(colours[FixedClass.SubjectColour.MATHS.name], FixedClass.SubjectColour.MATHS.label)
        self.assertEqual(colours[FixedClass.SubjectColour.FREE.name], FixedClass.SubjectColour.FREE.label)

    def test_teacher_timetable_view_correct_response(self):
        """
        Unit test that the context returned by a GET request to the teacher_timetable_view function, containing the
        relevant timetable etc.
        """
        self.client.login(username='dummy_teacher', password='dt123dt123')
        url = reverse('teacher_timetable_view', kwargs={"teacher_id": 6})  # Timetable for Greg Thebaker
        response = self.client.get(url)

        # Test teacher context
        teacher = response.context["teacher"]
        self.assertIsInstance(teacher, Teacher)
        self.assertEqual(teacher.firstname, "Greg")

        # Test timetable content
        timetable = response.context["timetable"]
        monday_period_one = timetable[TimetableSlot.PeriodStart.PERIOD_ONE.value][TimetableSlot.WeekDay.MONDAY.value]
        self.assertIsInstance(monday_period_one, FixedClass)
        self.assertEqual(monday_period_one.subject_name, FixedClass.SubjectColour.FRENCH.name)
        free_period = timetable[TimetableSlot.PeriodStart.PERIOD_TWO.value][TimetableSlot.WeekDay.MONDAY.value]
        self.assertEqual(free_period, FixedClass.SubjectColour.FREE.name)  # string returned, not a FixedClass instance

        # Test the colours context
        colours = response.context["colours"]
        self.assertIsInstance(colours, dict)
        self.assertEqual(colours[Pupil.YearGroup.ONE.value], Pupil.YearGroup.ONE.label)
        self.assertEqual(colours[FixedClass.SubjectColour.FREE.name], FixedClass.SubjectColour.FREE.value)
        self.assertEqual(colours[FixedClass.SubjectColour.LUNCH.name], FixedClass.SubjectColour.LUNCH.value)
