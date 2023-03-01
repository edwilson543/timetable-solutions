"""Unit tests for teacher operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.teachers import exceptions, operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewTeacher:
    @pytest.mark.parametrize("teacher_id", [1, None])
    def test_creates_teacher_in_db_for_valid_params(self, teacher_id: int | None):
        # Make a school for the teacher to teach at
        school = data_factories.School()

        # Try creating teacher using create_new
        operations.create_new_teacher(
            school_id=school.school_access_key,
            teacher_id=teacher_id,
            firstname="test",
            surname="testson",
            title="mr",
        )

        # Check teacher was created
        all_teachers = models.Teacher.objects.all()
        assert all_teachers.count() == 1
        db_teacher = all_teachers.get()

        assert db_teacher.teacher_id == 1
        assert db_teacher.firstname == "test"
        assert db_teacher.surname == "testson"
        assert db_teacher.title == "mr"

    def test_raises_when_teacher_id_not_unique_for_school(self):
        # Make a teacher to occupy an id value
        teacher = data_factories.Teacher()

        # Try making a teacher with the same school / id
        with pytest.raises(exceptions.CouldNotCreateTeacher):
            operations.create_new_teacher(
                school_id=teacher.school.school_access_key,
                teacher_id=teacher.teacher_id,
                firstname="test-2",
                surname="test-2",
                title="mrs",
            )


@pytest.mark.django_db
class TestUpdateTeacher:
    def test_updates_teacher_in_db_for_valid_params(self):
        teacher = data_factories.Teacher()

        operations.update_teacher(
            teacher=teacher, firstname="test", surname="testnameson", title="mr"
        )

        assert teacher.firstname == "test"
        assert teacher.surname == "testnameson"
        assert teacher.title == "mr"


@pytest.mark.django_db
class TestDeleteTeacher:
    def test_delete_teacher_successful(self):
        teacher = data_factories.Teacher()

        deleted = operations.delete_teacher(teacher)

        assert deleted == (1, {"data.Teacher": 1})
        with pytest.raises(models.Teacher.DoesNotExist):
            teacher.refresh_from_db()

    def test_delete_teacher_unsuccessful_if_has_lessons(self):
        lesson = data_factories.Lesson()

        with pytest.raises(exceptions.CouldNotDeleteTeacher):
            operations.delete_teacher(lesson.teacher)
