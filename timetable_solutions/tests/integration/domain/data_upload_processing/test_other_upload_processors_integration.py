"""
Module containing integration tests for:
- TeacherFileUploadProcessor
- ClassroomFileUploadProcessor
- YearGroupFileUploadProcessor
- PupilFileUploadProcessor
"""

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase


# Local application imports
from base_files.settings.base_settings import BASE_DIR
from data import models
from domain import data_upload_processing
from tests.input_settings import TEST_DATA_DIR


class TestFileUploadProcessorIndependentFilesValidUploads(TestCase):
    """
    Tests for the file uploads that depend on no existing data in the database,
    using files with valid content / structure.
    These are:
        - Teacher, Classroom, YearGroup
    """

    fixtures = ["user_school_profile.json"]
    valid_uploads = TEST_DATA_DIR / "valid_uploads"

    # TESTS FOR VALID FILE UPLOADS
    def test_upload_teachers_to_database_valid_upload(self):
        """Test that the FileUploadProcessor can upload the teacher csv file and use it to populate database"""
        # Set test parameters
        with open(self.valid_uploads / "teachers.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.TeacherFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 11)

        # Test the database is as expected
        all_teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_teachers.count(), 11)
        greg = models.Teacher.objects.get_individual_teacher(
            school_id=123456, teacher_id=6
        )
        self.assertIsInstance(greg, models.Teacher)
        self.assertEqual(greg.firstname, "Greg")
        self.assertEqual(greg.surname, "Thebaker")

    def test_upload_classrooms_to_database_valid_upload(self):
        """Test that the FileUploadProcessor can upload the classroom csv file and use it to populate database"""

        # Set test parameters
        with open(self.valid_uploads / "classrooms.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.ClassroomFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 12)

        # Test that the database is as expected
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_classrooms.count(), 12)
        room = models.Classroom.objects.get_individual_classroom(
            school_id=123456, classroom_id=11
        )
        self.assertEqual(room.room_number, 40)

    def test_upload_year_groups_to_database_valid_upload(self):
        """Test that the FileUploadProcessor can upload the year_group csv file and use it to populate database"""

        # Set test parameters
        with open(self.valid_uploads / "year_groups.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.YearGroupFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 3)

        # Test that the database is as expected
        all_ygs = models.YearGroup.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_ygs.count(), 3)

        expected_year_groups = ["1", "2", "Reception"]
        actual_year_groups = list(all_ygs.values_list("year_group", flat=True))
        self.assertEqual(expected_year_groups, actual_year_groups)


class TestPupilFileUploadProcessor(TestCase):
    """
    Test for pupil file uploads, which needs the YearGroup database table populated.
    """

    fixtures = ["user_school_profile.json", "year_groups.json"]
    valid_uploads = TEST_DATA_DIR / "valid_uploads"

    def test_upload_pupils_to_database_valid_upload(self):
        """Test that the FileUploadProcessor can upload the pupil csv file and use it to populate database"""
        # Set test parameters
        with open(self.valid_uploads / "pupils.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.PupilFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 6)

        # Test that the database is as expected
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(all_pupils.count(), 6)
        teemu = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=5)
        self.assertEqual(teemu.firstname, "Teemu")
        self.assertEqual(teemu.surname, "Pukki")


class TestFileUploadProcessorInvalidPupilUploads(TestCase):
    """
    Tests for pupil file uploads with invalid content / structure.
    """

    fixtures = ["user_school_profile.json", "year_groups.json"]
    invalid_uploads = TEST_DATA_DIR / "invalid_uploads"

    def run_test_for_pupils_with_error_in_row_n(
        self,
        filename: str,
        row_n: int,
        expected_error_snippet: str | None = None,
    ) -> None:
        """
        Utility test that can be run for different files, all with different types of error in row n.
        Note we always test the atomicity of uploads - we want none or all rows of the uploaded file to be
        processed into the database.
        """
        # Set test parameters
        with open(self.invalid_uploads / filename, "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.PupilFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Check the outcome
        self.assertFalse(upload_processor.upload_successful)
        if expected_error_snippet is None:
            expected_error_snippet = f"Could not interpret values in row {row_n}"
        self.assertIn(expected_error_snippet, upload_processor.upload_error_message)

        # Check NO pupils have been uploaded to the database
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(all_pupils.count(), 0)

    def test_upload_pupils_file_missing_id(self):
        """
        Unit test that a pupils file whose only error is a missing id halfway down will be rejected for processing.
        """
        # Set test parameters
        filename = "pupils_missing_id.csv"

        # Execute test
        self.run_test_for_pupils_with_error_in_row_n(filename=filename, row_n=4)

    def test_upload_pupils_file_missing_surname(self):
        """
        Unit test that a pupils file whose only error is a missing surname will be rejected for processing.
        Note that the missing surname initially gets replace by the nan-handler, and later filtered out before trying
        to create a Pupil instance.
        """
        # Set test parameters
        filename = "pupils_missing_surname.csv"

        # Execute test
        self.run_test_for_pupils_with_error_in_row_n(filename=filename, row_n=4)

    def test_upload_pupils_file_invalid_type_string_instead_of_int(self):
        """
        Unit test that a pupils file with a STRING in the id column is rejected
        """
        # Set test parameters
        filename = "pupils_string_in_id_column.csv"

        # Execute test
        self.run_test_for_pupils_with_error_in_row_n(filename=filename, row_n=6)

    def test_upload_pupils_file_non_existent_year_group(self):
        """
        Unit test that a pupils file with a non-existent year group (3.8) is rejected
        """
        # Set test parameters
        filename = "pupils_non_existent_year_group.csv"

        # Execute test
        self.run_test_for_pupils_with_error_in_row_n(
            filename=filename,
            row_n=6,
            expected_error_snippet="Row 6 of your file referenced a",  # ...
        )


class TestFileUploadProcessorInvalidMiscellaneous(TestCase):
    """
    Tests for attempting to upload files which fall in one of the following categories:
        - Incorrect file type (e.g. .png)
        - Bad csv structure (e.g. certain rows have more columns than in the headers)
        - Simulate a resubmitted form -> should not upload the same data twice
    """

    fixtures = ["user_school_profile.json", "year_groups.json"]
    valid_uploads = TEST_DATA_DIR / "valid_uploads"
    invalid_uploads = TEST_DATA_DIR / "invalid_uploads"

    def test_uploading_a_png_file(self):
        """
        Unit test that the upload processor will reject a file that does not have the csv extension
        """
        # Set test parameters
        png_filepath = BASE_DIR / "interfaces" / "base_static" / "img" / "favicon.png"
        with open(png_filepath, "rb") as png_file:
            upload_file = SimpleUploadedFile(png_file.name, png_file.read())

        # Execute test unit
        processor = data_upload_processing.PupilFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Check outcome
        self.assertIsNotNone(processor.upload_error_message)
        self.assertIn(".png", processor.upload_error_message)

        # Check no pupils were created...
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(all_pupils.count(), 0)

    def test_uploading_a_bad_csv_file(self):
        """
        Test that a file that has random values is undefined columns gets rejected
        """
        # Set test parameters
        test_filepath = self.invalid_uploads / "pupils_bad_column_structure.csv"
        with open(test_filepath, "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Execute test unit
        processor = data_upload_processing.PupilFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Check outcome
        self.assertIsNotNone(processor.upload_error_message)
        self.assertIn("Bad file structure", processor.upload_error_message)

        # Check no pupils were created...
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(all_pupils.count(), 0)

    def test_resubmitted_upload_is_rejected(self):
        """
        Test that if we successfully upload a pupils file, if we then 'resubmit the form', the data is the
        processed twice.
        """
        # Set test parameters
        test_filepath = self.valid_uploads / "pupils.csv"
        with open(test_filepath, "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        processor = data_upload_processing.PupilFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
            attempt_upload=False,
        )

        # Execute test unit one
        processor._upload_file_content(file=upload_file)

        # Check outcome one
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(all_pupils.count(), 6)
        self.assertIsNone(processor.upload_error_message)

        # Execute test unit two - 'resubmit the form'
        # Note 1 mangles the file (only in test) so we re-read it
        with open(test_filepath, "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
        processor._upload_file_content(file=upload_file)

        # Check outcome one
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        self.assertEqual(all_pupils.count(), 6)
        self.assertIsNotNone(processor.upload_error_message)
        self.assertIn("not unique", processor.upload_error_message)
