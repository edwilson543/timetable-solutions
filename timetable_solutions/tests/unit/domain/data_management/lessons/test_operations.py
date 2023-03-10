"""Unit tests for the Lesson model operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.lesson import operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewLesson:
    def test_create_new_valid_lesson(self):
        # Get some data to make the lesson with
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)
        pupil = data_factories.Pupil(school=school)
        user_defined_slot = data_factories.TimetableSlot(
            school=school, relevant_year_groups=(pupil.year_group,)
        )

        # Try creating the lesson
        lesson = operations.create_new_lesson(
            school_id=school.school_access_key,
            lesson_id="test",
            subject_name="test",
            total_required_slots=4,
            total_required_double_periods=2,
            teacher_id=teacher.teacher_id,
            classroom_id=classroom.classroom_id,
            pupils=models.Pupil.objects.all(),
            user_defined_time_slots=models.TimetableSlot.objects.all(),
        )

        # Check lesson was created
        assert models.Lesson.objects.get() == lesson

        # Check lesson fields are as expected
        assert lesson.school == school
        assert lesson.lesson_id == "test"
        assert lesson.subject_name == "test"
        assert lesson.total_required_slots == 4
        assert lesson.total_required_double_periods == 2
        assert lesson.teacher == teacher
        assert lesson.classroom == classroom
        assert lesson.pupils.get() == pupil
        assert lesson.user_defined_time_slots.get() == user_defined_slot

    def test_raises_when_teacher_does_not_exist(self):
        school = data_factories.School()

        with pytest.raises(operations.UnableToCreateLesson) as exc:
            operations.create_new_lesson(
                school_id=school.school_access_key,
                lesson_id="test",
                subject_name="test",
                total_required_slots=4,
                total_required_double_periods=2,
                teacher_id=1,  # Does not exist
            )

        assert "Teacher with id 1 does not exist!" in exc.value.human_error_message

    def test_raises_when_classroom_does_not_exist(self):
        school = data_factories.School()

        with pytest.raises(operations.UnableToCreateLesson) as exc:
            operations.create_new_lesson(
                school_id=school.school_access_key,
                lesson_id="test",
                subject_name="test",
                total_required_slots=4,
                total_required_double_periods=2,
                classroom_id=1,  # Does not exist
            )

        assert "Classroom with id 1 does not exist!" in exc.value.human_error_message

    def test_raises_when_lesson_id_not_unique(self):
        lesson = data_factories.Lesson()

        with pytest.raises(operations.UnableToCreateLesson) as exc:
            operations.create_new_lesson(
                school_id=lesson.school.school_access_key,
                lesson_id=lesson.lesson_id,
                subject_name="test",
                total_required_slots=4,
                total_required_double_periods=2,
            )

        assert (
            "Could not create lesson with the given data."
            in exc.value.human_error_message
        )

    def test_raises_when_double_slots_exceeds_single_slots(self):
        school = data_factories.School()

        with pytest.raises(operations.UnableToCreateLesson) as exc:
            operations.create_new_lesson(
                school_id=school.school_access_key,
                lesson_id="Maths-A",
                subject_name="test",
                total_required_slots=2,
                total_required_double_periods=5,
            )

        assert (
            "Could not create lesson with the given data."
            in exc.value.human_error_message
        )
