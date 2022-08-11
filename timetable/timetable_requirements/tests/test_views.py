"""Unit tests for views of the timetable_requirements app"""

# Standard library imports
from pathlib import Path

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

# Local application imports
from timetable_selector.models import Teacher


class TestFileUploadViews(TestCase):
    test_data_folder = Path(__file__).parents[1] / "test_data"

    def test_teacher_list_upload_view_file_uploads_successfully(self):
        """Unit test that simulating a csv file upload successfully populates the central database."""
        # Set the state of the test database
        with open(self.test_data_folder / "teachers.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            url = reverse("teacher_list")  # Corresponds to TeacherListUploadView
            self.client.post(url, data={"teacher_list": upload_file})

        # Test that the database is as expected
        all_teachers = Teacher.objects.all()
        self.assertEqual(len(all_teachers), 11)
        greg = Teacher.objects.get(teacher_id=6)
        self.assertIsInstance(greg, Teacher)
        self.assertEqual(greg.firstname, "Greg")
        self.assertEqual(greg.surname, "Thebaker")
