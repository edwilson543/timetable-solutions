"""Unit tests for views of the timetable_requirements app"""

# Standard library imports
from datetime import time, timedelta

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

# Local application imports
from data import models
from base_files.settings import BASE_DIR


class TestFileUploadViews(TestCase):

    fixtures = ["user_school_profile.json"]
    test_data_folder = BASE_DIR / "tests" / "test_data"

    def upload_test_file(self, filename: str, url_data_name: str) -> None:
        """
        :param filename: the name of the csv file we are simulating the upload of
        :param url_data_name: the url extension for the given test file upload (also dict key in the data post request)
        """
        with open(self.test_data_folder / filename, "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            url = reverse(url_data_name)  # Corresponds to TeacherListUploadView
            self.client.post(url, data={url_data_name: upload_file})

    def test_teacher_list_upload_view_file_uploads_successfully(self):
        """Unit test that simulating a csv file upload of teachers successfully populates the central database."""
        self.client.login(username="dummy_teacher", password="dt123dt123")
        self.upload_test_file(filename="teachers.csv", url_data_name="teacher_list")

        # Test that the database is as expected
        school = models.School.objects.get(school_access_key=123456)
        all_teachers = models.Teacher.objects.filter(school=school)
        self.assertEqual(len(all_teachers), 11)
        greg = models.Teacher.objects.get(teacher_id=6)
        self.assertEqual(greg.firstname, "Greg")
        self.assertEqual(greg.surname, "Thebaker")

    def test_teacher_list_upload_view_file_unsuccessful_with_invalid_file(self):
        """
        We try uploading the demo pupils file, to check that this does not work, and also that the database
        is unaffected.
        """
        self.client.login(username="dummy_teacher", password="dt123dt123")
        # Try uploading the wrong file (pupils.csv)
        self.upload_test_file(filename="pupils.csv", url_data_name="teacher_list")

        # Assert that nothing has happened
        school = models.School.objects.get(school_access_key=123456)
        self.assertEqual(len(models.Teacher.objects.filter(school=school)), 0)

    def test_pupil_list_upload_view_file_uploads_successfully(self):
        """Unit test that simulating a csv file upload of pupils successfully populates the central database."""
        self.client.login(username="dummy_teacher", password="dt123dt123")
        self.upload_test_file(filename="pupils.csv", url_data_name="pupil_list")

        # Test that the database is as expected
        school = models.School.objects.get(school_access_key=123456)
        all_pupils = models.Pupil.objects.filter(school=school)
        self.assertEqual(len(all_pupils), 6)
        teemu = models.Pupil.objects.get(pupil_id=5)
        self.assertEqual(teemu.firstname, "Teemu")
        self.assertEqual(teemu.surname, "Pukki")

    def test_pupil_list_upload_view_file_unsuccessful_with_invalid_file(self):
        """
        We try uploading the demo teachers file, to check that this does not work, and also that the database
        is unaffected.
        """
        # Try uploading the wrong file (teachers.csv)
        self.client.login(username="dummy_teacher", password="dt123dt123")
        self.upload_test_file(filename="teachers.csv", url_data_name="pupil_list")

        # Assert that nothing has happened
        school = models.School.objects.get(school_access_key=123456)
        self.assertEqual(len(models.Pupil.objects.filter(school=school)), 0)

    def test_classroom_list_upload_view_file_uploads_successfully(self):
        """Unit test that simulating a csv file upload of classrooms successfully populates the central database."""
        self.client.login(username="dummy_teacher", password="dt123dt123")
        self.upload_test_file(filename="classrooms.csv", url_data_name="classroom_list")

        # Test that the database is as expected
        all_classrooms = models.Classroom.objects.get_all_school_classrooms(school_id=123456)
        self.assertEqual(len(all_classrooms), 12)
        room = models.Classroom.objects.get_individual_classroom(school_id=123456, classroom_id=11)
        self.assertEqual(room.room_number, 40)

    def test_timetable_structure_list_upload_view_file_uploads_successfully(self):
        """Unit test that simulating a csv file upload of classrooms successfully populates the central database."""
        self.client.login(username="dummy_teacher", password="dt123dt123")
        self.upload_test_file(filename="timetable.csv", url_data_name="timetable_structure")

        # Test that the database is as expected
        school = models.School.objects.get(school_access_key=123456)
        all_slots = models.TimetableSlot.objects.filter(school=school)
        self.assertEqual(len(all_slots), 35)
        slot = models.TimetableSlot.objects.get(slot_id=1)
        self.assertEqual(slot.day_of_week, "MONDAY")
        self.assertEqual(slot.period_starts_at, time(hour=9))
        self.assertEqual(slot.period_duration, timedelta(hours=1))

    def test_unsolved_classes_list_upload_view_file_uploads_successfully(self):
        """
        Unit test that simulating a csv file upload of unsolved classes successfully populates the central database.
        Note that we first have to upload the pupils, teachers, timetable structure and classrooms.
        """
        self.client.login(username="dummy_teacher", password="dt123dt123")
        # First we need the pupils, teachers, classrooms and timetable structure
        self.upload_test_file(filename="teachers.csv", url_data_name="teacher_list")
        self.upload_test_file(filename="pupils.csv", url_data_name="pupil_list")
        self.upload_test_file(filename="timetable.csv", url_data_name="timetable_structure")
        self.upload_test_file(filename="classrooms.csv", url_data_name="classroom_list")
        # Now can upload the unsolved classes csv
        self.upload_test_file(filename="class_requirements.csv", url_data_name="unsolved_classes")

        # Test the database is as expected
        school = models.School.objects.get(school_access_key=123456)
        all_classes = models.UnsolvedClass.objects.filter(school=school)
        assert len(all_classes) == 12
        klass = models.UnsolvedClass.objects.get(class_id="YEAR_ONE_MATHS_A")

        self.assertQuerysetEqual(klass.pupils.all(), models.Pupil.objects.filter(pupil_id__in={1, 2}), ordered=False)
        self.assertEqual(klass.teacher, models.Teacher.objects.get(teacher_id=1))

    def test_fixed_classes_list_upload_view_file_uploads_successfully(self):
        """
        Unit test that simulating a csv file upload of fixed classes successfully populates the central database.
        Note that we first have to upload the pupils, teachers, timetable structure and classrooms.
        """
        self.client.login(username="dummy_teacher", password="dt123dt123")
        # First we need the pupils, teachers, classrooms and timetable structure
        self.upload_test_file(filename="teachers.csv", url_data_name="teacher_list")
        self.upload_test_file(filename="pupils.csv", url_data_name="pupil_list")
        self.upload_test_file(filename="timetable.csv", url_data_name="timetable_structure")
        self.upload_test_file(filename="classrooms.csv", url_data_name="classroom_list")
        # Now can upload the unsolved classes csv
        self.upload_test_file(filename="fixed_classes.csv", url_data_name="fixed_classes")

        # Test the database is as expected
        school = models.School.objects.get(school_access_key=123456)
        all_classes = models.FixedClass.objects.filter(school=school)
        assert len(all_classes) == 12
        pup_lunch = models.FixedClass.objects.get(class_id="LUNCH_PUPILS")
        self.assertQuerysetEqual(pup_lunch.pupils.all(), models.Pupil.objects.all(), ordered=False)
        teach_ten_lunch = models.FixedClass.objects.get(class_id="LUNCH_10")
        self.assertEqual(teach_ten_lunch.teacher, models.Teacher.objects.get(teacher_id=10))
