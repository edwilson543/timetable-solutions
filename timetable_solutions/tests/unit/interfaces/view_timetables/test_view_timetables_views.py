"""
Module containing unit tests for the views in view_timetables app.
"""

# Standard library imports
import io

# Third party imports
import pandas as pd

# Django imports
from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse

# Local application imports
from constants.url_names import UrlName
from data import models
from domain.view_timetables.timetable_colours import TimetableColourAssigner


class TestViews(TestCase):
    """
    Test class for the view_timetables app.
    """

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    def test_selection_dashboard_response(self):
        """
        Test that the selection dashboard is being loaded along with the relevant summary stats.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.VIEW_TIMETABLES_DASH.value)

        # Execute test unit
        response = self.client.get(url)

        # Test the keys of the dict are the year groups
        assert response.status_code == 200
        assert response.context["has_solutions"]

    def test_pupil_navigator_response(self):
        """
        Test that the correct full list of pupils indexed by year group is returned by a get request to the
        pupil_navigator view. We test the data structures at successive depths of the nested context dictionary.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.PUPILS_NAVIGATOR.value)

        # Execute test unit
        response = self.client.get(url)

        # Test the keys of the dict are the year groups
        assert response.status_code == 200
        assert "year_groups" in response.context

    def test_teacher_navigator_response(self):
        """Test that the correct full list of teachers is returned, indexed by the first letter of their surname."""
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
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
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.PUPIL_TIMETABLE.value, kwargs={"pupil_id": 1})

        # Execute test unit
        response = self.client.get(url)

        # Test pupil context
        pupil = response.context["pupil"]
        self.assertIsInstance(pupil, models.Pupil)
        self.assertEqual(pupil.firstname, "John")
        self.assertEqual(pupil.year_group.year_group, "1")

        # Test timetable context
        timetable = response.context["timetable"]
        monday_period_one = timetable["09:00-10:00"][models.WeekDay.MONDAY.label]
        self.assertIsInstance(monday_period_one, models.Lesson)
        self.assertEqual(monday_period_one.subject_name, "MATHS")
        self.assertEqual(monday_period_one.classroom.building, "MB")
        free_period = timetable["12:00-13:00"][models.WeekDay.THURSDAY.label]
        # For free periods, the dictionary value is a string as opposed to a Lesson instance
        self.assertEqual(free_period, "FREE")

        # Test colours context
        colours = response.context["class_colours"]
        default_colour_ranking = TimetableColourAssigner._colour_ranking
        self.assertIsInstance(colours, dict)
        self.assertEqual(
            colours["MATHS"], default_colour_ranking[1]
        )  # [1] since maths' rank is 1 on pupil's timetable
        self.assertEqual(
            colours[TimetableColourAssigner.Colour.FREE.name],
            TimetableColourAssigner.Colour.FREE.value,
        )

    def test_teacher_timetable_view_correct_response(self):
        """
        Unit test that the context returned by a GET request to the teacher_timetable_view function, containing the
        relevant timetable etc.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(
            UrlName.TEACHER_TIMETABLE.value, kwargs={"teacher_id": 6}
        )  # Timetable for Greg Thebaker

        # Execute test unit
        response = self.client.get(url)

        # Test teacher context
        teacher = response.context["teacher"]
        self.assertIsInstance(teacher, models.Teacher)
        self.assertEqual(teacher.firstname, "Greg")

        # Test timetable content
        timetable = response.context["timetable"]
        monday_period_one = timetable["09:00-10:00"][models.WeekDay.MONDAY.label]
        self.assertIsInstance(monday_period_one, models.Lesson)
        self.assertEqual(monday_period_one.subject_name, "FRENCH")
        free_period = timetable["10:00-11:00"][models.WeekDay.MONDAY.label]
        self.assertEqual(free_period, "FREE")

        # Test the colours context
        colours = response.context["year_group_colours"]
        default_colour_ranking = TimetableColourAssigner._colour_ranking
        self.assertIsInstance(colours, dict)
        self.assertEqual(colours["1"], default_colour_ranking[0])
        self.assertEqual(
            colours[TimetableColourAssigner.Colour.FREE.name],
            TimetableColourAssigner.Colour.FREE.value,
        )
        self.assertEqual(colours["LUNCH"], TimetableColourAssigner.Colour.MEAL.value)

    # TESTS FOR CSV FILE DOWNLOADS
    def test_pupil_timetable_csv_download_as_expected(self):
        """
        Unit tests that the file provided by the url for pupil csv timetable downloads is as expected.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.PUPIL_TT_CSV_DOWNLOAD.value, kwargs={"pupil_id": 1})

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        headers = response.headers
        self.assertEqual(headers["Content-Type"], "text/csv")
        self.assertEqual(
            headers["Content-Disposition"],
            "attachment; filename=Timetable-John-Smith.csv",
        )

        timetable_buffer = io.BytesIO(response.content)
        timetable = pd.read_csv(timetable_buffer, index_col="Time")

        self.assertEqual(timetable.isnull().sum().sum(), 0)
        self.assertEqual(
            list(timetable.columns),
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        )
        self.assertEqual(timetable.index.name, "Time")

        # Check random specific element
        thursday_two_pm = timetable.loc["14:00-15:00", "Thursday"]
        self.assertEqual(thursday_two_pm, "Maths")

    def test_teacher_timetable_csv_download_as_expected(self):
        """
        Unit tests that the file provided by the url for teacher csv timetable downloads is as expected.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.TEACHER_TT_CSV_DOWNLOAD.value, kwargs={"teacher_id": 1})

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        headers = response.headers
        self.assertEqual(headers["Content-Type"], "text/csv")
        self.assertEqual(
            headers["Content-Disposition"],
            "attachment; filename=Timetable-Theresa-May.csv",
        )

        timetable_buffer = io.BytesIO(response.content)
        timetable = pd.read_csv(timetable_buffer, index_col="Time")

        self.assertEqual(timetable.isnull().sum().sum(), 0)
        self.assertEqual(
            list(timetable.columns),
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        )
        self.assertEqual(timetable.index.name, "Time")

        # Check random specific element
        tuesday_ten_am = timetable.loc["10:00-11:00", "Tuesday"]
        self.assertEqual(tuesday_ten_am, "French")

    # TESTS FOR PDF DOWNLOADS
    def test_pupil_timetable_pdf_download_as_expected(self):
        """
        Unit tests that the file provided by the url for pupil pdf timetable downloads is as expected.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.PUPIL_TT_PDF_DOWNLOAD.value, kwargs={"pupil_id": 1})

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        headers = response.headers
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertEqual(
            headers["Content-Disposition"],
            "attachment; filename=Timetable-John-Smith.pdf",
        )

    def test_teacher_timetable_pdf_download_as_expected(self):
        """
        Unit tests that the file provided by the url for teacher pdf timetable downloads is as expected.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.TEACHER_TT_PDF_DOWNLOAD.value, kwargs={"teacher_id": 1})

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        headers = response.headers
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertEqual(
            headers["Content-Disposition"],
            "attachment; filename=Timetable-Theresa-May.pdf",
        )
