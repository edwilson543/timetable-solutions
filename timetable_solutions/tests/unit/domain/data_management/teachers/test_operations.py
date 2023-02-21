"""Unit tests for teacher operations"""

import pytest

from data import models
from domain.data_management.teachers import exceptions, operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewTeacher:
    def test_creates_teacher_in_db_for_valid_params(self):
        # Make a school for the teacher to teach at
        school = data_factories.School()

        # Try creating teacher using create_new
        teacher = operations.create_new_teacher(
            school_id=school.school_access_key,
            teacher_id=1,
            firstname="test",
            surname="test",
            title="mr",
        )

        # Check teacher was created
        all_teachers = models.Teacher.objects.all()
        assert all_teachers.count() == 1
        assert all_teachers.first() == teacher

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
class TestCreateNewTeacher:
    def test_updates_teacher_in_db_for_valid_params(self):
        teacher = data_factories.Teacher()

        operations.update_teacher(
            teacher=teacher, firstname="test", surname="testnameson", title="mr"
        )

        assert teacher.firstname == "test"
        assert teacher.surname == "testnameson"
        assert teacher.title == "mr"
