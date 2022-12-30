"""Module containing integration tests for the LessonFileUploadProcessor"""

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Local application imports
from data import models
from domain import data_upload_processing
from tests.input_settings import TEST_DATA_DIR


class TestLessonFileUploadProcessorValidUploads(TestCase):
    """
    Tests for the file uploads that depend on existing data in the database, hence requiring fixtures.
    All tests in this class use files with valid content / structure.
    """

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "pupils.json",
        "teachers.json",
        "timetable.json",
    ]
    valid_uploads = TEST_DATA_DIR / "valid_uploads"

    def test_upload_lessons_file_to_database_valid_upload(self):
        """
        Test that the LessonFileUploadProcessor can upload the lessons.cv csv file and use it to populate database
        """
        # Set test parameters
        with open(self.valid_uploads / "lessons.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.LessonFileUploadProcessor(
            csv_file=upload_file, school_access_key=123456
        )

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 24)

        # Test the database is as expected
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_lessons.count(), 24)

        total_solver_required_slots = sum(
            lesson.get_n_solver_slots_required() for lesson in all_lessons
        )
        self.assertEqual(total_solver_required_slots, 100)  # = (8 * 8) + (9 * 4)

        total_solver_required_doubles = sum(
            lesson.get_n_solver_double_periods_required() for lesson in all_lessons
        )
        self.assertEqual(total_solver_required_doubles, 36)

        total_user_defined_slots = sum(
            lesson.user_defined_time_slots.all().count() for lesson in all_lessons
        )
        self.assertEqual(total_user_defined_slots, 60)

        lessons_with_teachers = sum(
            1 for lessons in all_lessons if lessons.teacher is not None
        )
        self.assertEqual(lessons_with_teachers, 23)  # All 24, except for 'PUPILS_LUNCH'

        lessons_with_classrooms = sum(
            1 for lessons in all_lessons if lessons.classroom is not None
        )
        self.assertEqual(lessons_with_classrooms, 12)

        total_non_unique_pupils = sum(lesson.pupils.count() for lesson in all_lessons)
        self.assertEqual(
            total_non_unique_pupils, 24
        )  # 18 from actual lessons, 6 from 'PUPILS_LUNCH'

        # Spot check on one specific Lesson
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        self.assertQuerysetEqual(
            lesson.pupils.all(),
            models.Pupil.objects.filter(pupil_id__in={1, 2}),
            ordered=False,
        )
        self.assertEqual(
            lesson.teacher,
            models.Teacher.objects.get_individual_teacher(
                school_id=123456, teacher_id=1
            ),
        )


class TestLessonFileUploadProcessorInvalidUploads(TestCase):
    """
    Tests for invalid lesson file uploads with invalid content / structure.
    """

    fixtures = [
        "user_school_profile.json",
        "pupils.json",
        "teachers.json",
        "timetable.json",
        "classrooms.json",
    ]
    invalid_uploads = TEST_DATA_DIR / "invalid_uploads"

    def run_test_for_lesson_file_with_error(self, filename: str) -> str:
        """
        Utility test that can be run for different files, all with different types of error in row n.
        Note we always test the atomicity of uploads - we want none or all rows of the uploaded file to be
        processed into the database.
        :return the error message produced by the processor
        """
        # Set test parameters
        with open(self.invalid_uploads / filename, "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.LessonFileUploadProcessor(
            csv_file=upload_file, school_access_key=123456
        )

        # Check the outcome
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_lessons.count(), 0)
        self.assertTrue(not upload_processor.upload_successful)

        return upload_processor.upload_error_message

    def test_upload_lessons_file_which_references_a_non_existent_pupil(self):
        """
        Unit test that a lessons file which references a non-existent pupil is rejected
        """
        # Set test parameters
        filename = "lessons_non_existent_pupil.csv"

        # Execute test
        error_message = self.run_test_for_lesson_file_with_error(filename=filename)

        # Check outcome
        self.assertIn("No pupil", error_message)
        self.assertIn("7", error_message)  # The non-existent pupil

    def test_upload_lessons_file_which_references_a_non_existent_classroom(self):
        """
        Unit test that a lessons file which references a non-existent classroom is rejected
        """
        # Set test parameters
        filename = "lessons_non_existent_classroom.csv"

        # Execute test
        error_message = self.run_test_for_lesson_file_with_error(filename=filename)

        # Check outcome
        self.assertIn("Row 2", error_message)
        self.assertIn("does not exist", error_message)
