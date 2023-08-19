"""Unit tests for the Lesson model operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.lesson import operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewLesson:
    @pytest.mark.parametrize("specify_year_group", [True, False])
    def test_create_new_valid_lesson(self, specify_year_group: bool):
        # Get some data to make the lesson with
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)
        pupil = data_factories.Pupil(school=school)
        year_group = pupil.year_group if specify_year_group else None
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
            year_group=year_group,
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
        assert lesson.year_group == pupil.year_group
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

    def test_raises_when_specified_year_group_is_different_to_the_pupils(self):
        school = data_factories.School()
        pupil = data_factories.Pupil(school=school)
        year_group = data_factories.YearGroup(school=school)

        assert pupil.year_group != year_group

        pupils = models.Pupil.objects.all()

        with pytest.raises(operations.UnableToCreateLesson) as exc:
            operations.create_new_lesson(
                pupils=pupils,
                year_group=year_group,
                school_id=school.school_access_key,
                lesson_id="test",
                subject_name="test",
                total_required_slots=1,
                total_required_double_periods=0,
            )

        assert (
            "The pupils' year group is different to the year group specified"
            in exc.value.human_error_message
        )


@pytest.mark.django_db
class TestUpdateLesson:
    def test_updates_lesson_in_db(self):
        lesson = data_factories.Lesson()
        teacher = data_factories.Teacher(school=lesson.school)
        classroom = data_factories.Classroom(school=lesson.school)

        updated_lesson = operations.update_lesson(
            lesson,
            subject_name="Geography",
            teacher=teacher,
            classroom=classroom,
            total_required_slots=10,
            total_required_double_periods=5,
        )

        assert updated_lesson.subject_name == "Geography"
        assert updated_lesson.teacher == teacher
        assert updated_lesson.classroom == classroom
        assert updated_lesson.total_required_slots == 10
        assert updated_lesson.total_required_double_periods == 5


@pytest.mark.django_db
class TestDeleteLesson:
    def test_deletes_lesson_from_db(self):
        lesson = data_factories.Lesson()

        operations.delete_lesson(lesson)

        with pytest.raises(models.Lesson.DoesNotExist):
            lesson.refresh_from_db()
