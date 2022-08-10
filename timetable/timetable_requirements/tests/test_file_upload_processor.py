"""Module containing unit tests for the FileUploadProcessor"""

# Standard library imports
from pathlib import Path

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Local application imports
from ..file_upload_processor import FileUploadProcessor
from timetable_selector.models import Teacher


class TestFileUploadProcessor(TestCase):
    test_data_folder = Path(__file__).parents[1] / "test_data"

    def test_upload_teachers_to_database_valid_upload(self):
        """Unit test that the FileUploadProcessor is able to take a csv file and save it to the database."""
        with open(self.test_data_folder / "teachers.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
            upload_processor = FileUploadProcessor(
                csv_file=upload_file, csv_headers=["teacher_id", "firstname", "surname", "title"],
                id_column_name="teacher_id", model=Teacher)

        # Test that attribute 'upload_successful' has been set to True, indicating that everythin has worked
        self.assertTrue(upload_processor.upload_successful)

        # Test that the database is as expected
        all_teachers = Teacher.objects.all()
        self.assertEqual(len(all_teachers), 11)
        greg = Teacher.objects.get(teacher_id=6)
        self.assertIsInstance(greg, Teacher)
        self.assertEqual(greg.firstname, "Greg")
        self.assertEqual(greg.surname, "Thebaker")
