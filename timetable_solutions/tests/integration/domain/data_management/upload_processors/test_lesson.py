"""Module containing integration tests for the LessonFileUploadProcessor"""


# Standard library imports
import io

# Third party imports
import pytest

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile

# Local application imports
from data import models
from domain import data_management
from domain.data_management.constants import Header
from tests import data_factories, utils


@pytest.mark.django_db
class TestLessonFileUploadProcessorValidUploads:
    """Test that 'lesson' files can be processed into the db successfully."""

    def test_two_lessons_no_user_defined_slots_successful(self):
        # Make some data that the csv file will need to reference
        school = data_factories.School()

        teacher_a = data_factories.Teacher(school=school)
        teacher_b = data_factories.Teacher(school=school)

        classroom_a = data_factories.Classroom(school=school)
        classroom_b = data_factories.Classroom(school=school)

        yg = data_factories.YearGroup(school=school)
        pupil_0 = data_factories.Pupil(school=school, year_group=yg)
        pupil_1 = data_factories.Pupil(school=school, year_group=yg)

        # Get a csv file-like object
        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    teacher_a.teacher_id,
                    f"{pupil_0.pupil_id}; {pupil_1.pupil_id}",
                    classroom_a.classroom_id,
                    3,
                    0,
                    None,  # No user defined slots (default)
                ],
                [
                    "english-b",
                    "English",
                    teacher_b.teacher_id,
                    f"{pupil_0.pupil_id}; {pupil_1.pupil_id}",
                    classroom_b.classroom_id,
                    5,
                    1,
                    None,  # No user defined slots (default)
                ],
            ]
        )

        # Upload the file
        upload_file = SimpleUploadedFile("lessons.csv", csv_file.read())
        upload_processor = data_management.LessonFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Check basic outcome of upload
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 2

        # Check saved to db
        lessons = models.Lesson.objects.filter(school=school)
        assert lessons.count() == 2

        # Check each lesson instance
        lesson_a = lessons.get(lesson_id="maths-a")
        assert lesson_a.subject_name == "Maths"
        assert lesson_a.teacher == teacher_a
        assert lesson_a.classroom == classroom_a
        pupils = lesson_a.pupils.all()
        assert pupils.count() == 2 and pupil_0 in pupils and pupil_1 in pupils
        assert lesson_a.total_required_slots == 3
        assert lesson_a.total_required_double_periods == 0
        assert lesson_a.user_defined_time_slots.all().count() == 0

        lesson_b = lessons.get(lesson_id="english-b")
        assert lesson_b.subject_name == "English"
        assert lesson_b.teacher == teacher_b
        assert lesson_b.classroom == classroom_b
        pupils = lesson_b.pupils.all()
        assert pupils.count() == 2 and pupil_0 in pupils and pupil_1 in pupils
        assert lesson_b.total_required_slots == 5
        assert lesson_b.total_required_double_periods == 1
        assert lesson_b.user_defined_time_slots.all().count() == 0

    def test_one_lesson_with_user_defined_slots_successful(self):
        # Make some data that the csv file will need to reference
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        # Make some slots that will be 'user defined' for the given lesson
        slots = [
            data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))
            for _ in range(0, 3)
        ]
        slot_id_string = "".join(f"{slot.slot_id};" for slot in slots)

        # Get a csv file-like object
        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    teacher.teacher_id,
                    f"{pupil.pupil_id};",
                    classroom.classroom_id,
                    5,
                    1,
                    slot_id_string,
                ],
            ]
        )

        # Upload the file
        upload_file = SimpleUploadedFile("lessons.csv", csv_file.read())
        upload_processor = data_management.LessonFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Check basic outcome of upload
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 1

        # Check saved to db
        lessons = models.Lesson.objects.filter(school=school)
        assert lessons.count() == 1

        lesson = lessons.first()
        assert lesson.subject_name == "Maths"
        assert lesson.teacher == teacher
        assert lesson.classroom == classroom
        pupils = lesson.pupils.all()
        assert pupils.count() == 1 and pupil in pupils
        assert lesson.total_required_slots == 5
        assert lesson.total_required_double_periods == 1
        user_defined_slots = lesson.user_defined_time_slots.all()
        assert user_defined_slots.count() == 3
        for slot in slots:
            assert slot in user_defined_slots

    def test_lesson_without_classroom_successful(self):
        # Make some data that the csv file will need to reference
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        # Get a csv file-like object
        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    teacher.teacher_id,
                    f"{pupil.pupil_id};",
                    None,  # No classroom
                    7,
                    2,
                    None,  # No user defined slots (default)
                ],
            ]
        )

        # Upload the file
        upload_file = SimpleUploadedFile("lessons.csv", csv_file.read())
        upload_processor = data_management.LessonFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Check basic outcome of upload
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 1

        # Check saved to db
        lessons = models.Lesson.objects.filter(school=school)
        assert lessons.count() == 1

        lesson = lessons.first()
        assert lesson.subject_name == "Maths"
        assert lesson.teacher == teacher
        assert lesson.classroom is None
        pupils = lesson.pupils.all()
        assert pupils.count() == 1 and pupil in pupils
        assert lesson.total_required_slots == 7
        assert lesson.total_required_double_periods == 2
        assert lesson.user_defined_time_slots.all().count() == 0

    def test_lesson_without_teacher_successful(self):
        # Make some data that the csv file will need to reference
        school = data_factories.School()
        classroom = data_factories.Classroom(school=school)
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        # Get a csv file-like object
        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    None,  # No teacher
                    f"{pupil.pupil_id};",
                    classroom.classroom_id,
                    7,
                    2,
                    None,  # No user defined slots (default)
                ],
            ]
        )

        # Upload the file
        upload_file = SimpleUploadedFile("lessons.csv", csv_file.read())
        upload_processor = data_management.LessonFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Check basic outcome of upload
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 1

        # Check saved to db
        lessons = models.Lesson.objects.filter(school=school)
        assert lessons.count() == 1

        lesson = lessons.first()
        assert lesson.subject_name == "Maths"
        assert lesson.teacher is None
        assert lesson.classroom == classroom
        pupils = lesson.pupils.all()
        assert pupils.count() == 1 and pupil in pupils
        assert lesson.total_required_slots == 7
        assert lesson.total_required_double_periods == 2
        assert lesson.user_defined_time_slots.all().count() == 0


@pytest.mark.django_db
class TestLessonFileUploadProcessorInvalidUploads:
    """Tests for uploading 'lesson' files we expect to fail."""

    @staticmethod
    def run_test_for_lesson_file_with_error(
        csv_file: io.BytesIO, school: models.School
    ) -> str:
        """
        Run a boilerplate upload for a file we expect to error.
        :param csv_file: The file-like object we are going to try and upload.
        :param school: The school that this data will be associated with.
        :return: The error message produced by the processor.
        """
        # Upload the file
        upload_file = SimpleUploadedFile("lessons.csv", csv_file.read())
        upload_processor = data_management.LessonFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Run some basic checks
        all_lessons = models.Lesson.objects.filter(school_id=school.school_access_key)
        assert all_lessons.count() == 0
        assert not upload_processor.upload_successful

        return upload_processor.upload_error_message

    def test_file_referencing_non_existent_pupil_is_unsuccessful(self):
        # Make some data - note we do not make a pupil
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)

        non_existent_pupil_id = "1"

        # Make the erroneous csv file
        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    teacher.teacher_id,
                    f"{non_existent_pupil_id};",
                    classroom.classroom_id,
                    7,
                    2,
                    None,  # No user defined slots (default)
                ],
            ]
        )

        # Execute test
        error_message = self.run_test_for_lesson_file_with_error(
            csv_file, school=school
        )

        # Check outcome
        assert "No pupil" in error_message
        assert non_existent_pupil_id in error_message

    def test_file_referencing_non_existent_teacher_is_unsuccessful(self):
        # Make some data - note we do not make a pupil
        school = data_factories.School()
        classroom = data_factories.Classroom(school=school)
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        non_existent_teacher_id = "1"

        # Make the erroneous csv file
        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    f"{non_existent_teacher_id};",
                    f"{pupil.pupil_id};",
                    classroom.classroom_id,
                    7,
                    2,
                    None,  # No user defined slots (default)
                ],
            ]
        )

        # Execute test
        error_message = self.run_test_for_lesson_file_with_error(
            csv_file, school=school
        )

        # Check outcome
        assert "does not exist" in error_message
        assert "Row 1" in error_message

    def test_file_referencing_non_existent_classroom_is_unsuccessful(self):
        # Make some data - note we do not make a pupil
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        non_existent_classroom_id = "1"

        # Make the erroneous csv file
        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    f"{teacher.teacher_id};",
                    f"{pupil.pupil_id};",
                    f"{non_existent_classroom_id};",
                    7,
                    2,
                    None,  # No user defined slots (default)
                ],
            ]
        )

        # Execute test
        error_message = self.run_test_for_lesson_file_with_error(
            csv_file, school=school
        )

        # Check outcome
        assert "does not exist" in error_message
        assert "Row 1" in error_message

    def test_file_referencing_non_existent_slot_is_unsuccessful(self):
        # Make some data - note we do not make a pupil
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        non_existent_slot_id = "1"

        # Make the erroneous csv file
        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    f"{teacher.teacher_id};",
                    f"{pupil.pupil_id};",
                    f"{classroom.classroom_id};",
                    7,
                    2,
                    f"{non_existent_slot_id};",
                ],
            ]
        )

        # Execute test
        error_message = self.run_test_for_lesson_file_with_error(
            csv_file, school=school
        )

        # Check outcome
        assert "No timetable slot(s) with ids: {1} were found!" in error_message
