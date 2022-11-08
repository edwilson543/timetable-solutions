"""Unit tests for views of the data_upload app"""

# Standard library imports
from datetime import time, timedelta

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

# Local application imports
from constants.url_names import UrlName
from data import models
from tests.input_settings import TEST_DATA_DIR


class TestCaseWithUpload(TestCase):
    """Subclass of the TestCase class, capable of uploading test csv files (subclasses twice below)."""
    fixtures = ["user_school_profile.json"]

    def upload_test_file(self, filename: str, url_data_name: UrlName) -> HttpResponse:
        """
        :param filename: the name of the csv file we are simulating the upload of
        :param url_data_name: the url extension for the given test file upload (also dict key in the data post request)
        """
        self.client.login(username="dummy_teacher", password="dt123dt123")
        with open((TEST_DATA_DIR / "valid_uploads" / filename), "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
        url = reverse(url_data_name)
        response = self.client.post(url, data={url_data_name: upload_file})
        return response


class TestIndependentFileUploadViews(TestCaseWithUpload):
    """
    Unit tests for the views controlling the upload of files which do not depend on the prior success of earlier
    uploads
    """

    def test_teacher_list_upload_view_file_uploads_successfully(self):
        """
        Unit test for the TeacherListUpload View, that simulating a csv file upload of teachers successfully populates
        the database.
        """
        # Execute test unit
        self.upload_test_file(filename="teachers.csv", url_data_name=UrlName.TEACHER_LIST_UPLOAD.value)

        # Test that the database is as expected
        all_teachers = models.Teacher.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_teachers), 11)
        greg = models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=6)
        self.assertEqual(greg.firstname, "Greg")
        self.assertEqual(greg.surname, "Thebaker")

    def test_teacher_list_upload_view_file_unsuccessful_with_invalid_file(self):
        """
        Unit test for the TeacherListUpload View. We try uploading the demo pupils file, to check that this does not
        work, and also that the database is unaffected.
        """
        # Try uploading the wrong file (pupils.csv)
        response = self.upload_test_file(
            filename="class_requirements.csv", url_data_name=UrlName.TEACHER_LIST_UPLOAD.value)

        # Check outcome
        self.assertEqual(len(models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)), 0)
        message = list(response.context["messages"])[0].message
        assert "Input file headers" in message

    def test_pupil_list_upload_view_file_uploads_successfully(self):
        """
        Unit test for PupilListUpload View, that simulating a csv file upload of pupils successfully populates the
        database.
        """
        # Execute test unit
        self.upload_test_file(filename="pupils.csv", url_data_name=UrlName.PUPIL_LIST_UPLOAD.value)

        # Test that the database is as expected
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_pupils), 6)
        teemu = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=5)
        self.assertEqual(teemu.firstname, "Teemu")
        self.assertEqual(teemu.surname, "Pukki")

    def test_pupil_list_upload_view_file_unsuccessful_with_invalid_file(self):
        """
        Unit test for PupilListUpload. We try uploading the demo teachers file, to check that this does not work,
        and also that the database is unaffected.
        """
        # Try uploading the wrong file (teachers.csv)
        response = self.upload_test_file(filename="teachers.csv", url_data_name=UrlName.PUPIL_LIST_UPLOAD.value)

        # Assert that nothing has happened
        self.assertEqual(len(models.Pupil.objects.get_all_instances_for_school(school_id=123456)), 0)
        message = list(response.context["messages"])[0].message
        assert "Input file headers" in message

    def test_classroom_list_upload_view_file_uploads_successfully(self):
        """
        Unit test for the ClassrromListView, that simulating a csv file upload of classrooms successfully populates the
        database.
        """
        self.upload_test_file(filename="classrooms.csv", url_data_name=UrlName.CLASSROOM_LIST_UPLOAD.value)

        # Test that the database is as expected
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_classrooms), 12)
        room = models.Classroom.objects.get_individual_classroom(school_id=123456, classroom_id=11)
        self.assertEqual(room.room_number, 40)

    def test_timetable_structure_list_upload_view_file_uploads_successfully(self):
        """
        Unit test for the TimetableStructureUpload view, that simulating a csv file upload of tt slots successfully
        populates the database.
        """
        self.upload_test_file(filename="timetable.csv", url_data_name=UrlName.TIMETABLE_STRUCTURE_UPLOAD.value)

        # Test that the database is as expected
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(len(all_slots), 35)
        slot = models.TimetableSlot.objects.get_individual_timeslot(school_id=123456, slot_id=1)
        self.assertEqual(slot.day_of_week, 1)
        self.assertEqual(slot.period_starts_at, time(hour=9))
        self.assertEqual(slot.period_duration, timedelta(hours=1))

    def test_file_upload_page_redirects_logged_out_users_who_submit_get_requests(self):
        """
        Unit test that an anonymous user will be redirected to login, when submitting a GET request to the data
        upload page
        """
        # Set test parameters
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit - note no login
        response = self.client.get(url)

        # Check outcome
        self.assertIn("users/accounts/login", response.url)


class TestDependentFileUploadViews(TestCaseWithUpload):
    """Unit tests for the views controlling the upload of files which depend on the prior success of earlier uploads"""

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json"]

    def test_unsolved_classes_list_upload_view_file_uploads_successfully(self):
        """
        Unit test for the UnsolvedClassUpload View, that simulating a csv file upload of unsolved classes successfully
        populates the database.
        """
        self.upload_test_file(filename="class_requirements.csv", url_data_name=UrlName.UNSOLVED_CLASSES_UPLOAD.value)

        # Test the database is as expected
        all_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        assert len(all_classes) == 12
        klass = models.UnsolvedClass.objects.get_individual_unsolved_class(school_id=123456,
                                                                           class_id="YEAR_ONE_MATHS_A")
        self.assertQuerysetEqual(klass.pupils.all(), models.Pupil.objects.filter(pupil_id__in={1, 2}), ordered=False)
        self.assertEqual(klass.teacher, models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=1))

    def test_fixed_classes_list_upload_view_file_uploads_successfully(self):
        """
        Unit test for the FixedClassUploadView, that simulating a csv file upload of fixed classes successfully
        populates the database.
        """
        self.upload_test_file(filename="fixed_classes.csv", url_data_name=UrlName.FIXED_CLASSES_UPLOAD.value)

        # Test the database is as expected
        all_classes = models.FixedClass.objects.get_all_instances_for_school(school_id=123456)
        assert len(all_classes) == 12
        pup_lunch = models.FixedClass.objects.get_individual_fixed_class(school_id=123456, class_id="LUNCH_PUPILS")
        self.assertQuerysetEqual(pup_lunch.pupils.all(),
                                 models.Pupil.objects.get_all_instances_for_school(school_id=123456), ordered=False)
        teach_ten_lunch = models.FixedClass.objects.get_individual_fixed_class(school_id=123456, class_id="LUNCH_10")
        self.assertEqual(teach_ten_lunch.teacher,
                         models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=10))
