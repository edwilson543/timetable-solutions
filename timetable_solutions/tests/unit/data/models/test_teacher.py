"""
Unit tests for methods on the Teacher class
"""

# Third party imports
import pytest

# Django imports
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import models
from tests import data_factories


@pytest.mark.django_db
class TestTeacherFactories:
    def test_create_new_valid_teacher(self):
        """
        Tests that we can create and save a Teacher via the create_new method
        """
        # Make a school for the teacher to teach at
        school = data_factories.School()

        # Try creating teacher using create_new
        teacher = models.Teacher.create_new(
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

    def test_create_new_fails_when_teacher_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Teachers with the same id / school, due to unique_together on the Meta class
        """
        # Make a teacher to occupy an id value
        teacher = data_factories.Teacher()

        # Try making a teacher with the same school / id
        with pytest.raises(IntegrityError):
            models.Teacher.create_new(
                school_id=teacher.school.school_access_key,
                teacher_id=teacher.teacher_id,
                firstname="test-2",
                surname="test-2",
                title="mrs",
            )

    def test_delete_all_instances_for_school_successful_when_no_lessons(self):
        """
        Test that we can successfully delete all teachers associated with a school, when there are no Lessons
        instances referencing the teachers as foreign keys.
        """
        # Get a teacher
        teacher = data_factories.Teacher()

        # Delete all the teachers at this teacher's school
        outcome = models.Teacher.delete_all_instances_for_school(
            school_id=teacher.school.school_access_key
        )

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.Teacher"] == 1

        all_teachers = models.Teacher.objects.all()
        assert all_teachers.count() == 0

    def test_delete_all_instances_for_school_unsuccessful_when_attached_to_lessons(
        self,
    ):
        """
        Test that we cannot delete all teachers associated with a school, when there is at least one Lesson
        referencing the teachers we are trying to delete.
        """
        # Make a lesson with a teacher
        lesson = data_factories.Lesson()
        assert lesson.teacher

        # Try deleting all the lessons for a school
        with pytest.raises(ProtectedError):
            models.Teacher.delete_all_instances_for_school(
                school_id=lesson.school.school_access_key
            )


@pytest.mark.django_db
class TestTeacherMutators:
    @pytest.mark.parametrize("firstname", ["testname", None])
    @pytest.mark.parametrize("surname", ["testnameson", None])
    @pytest.mark.parametrize("title", ["mr", None])
    def test_update_updates_teacher_details_with_params(
        self, firstname: str, surname: str, title: str
    ):
        teacher = data_factories.Teacher()

        teacher.update(firstname=firstname, surname=surname, title=title)

        expected_firstname = firstname or teacher.firstname
        expected_surname = surname or teacher.surname
        expected_title = title or teacher.title

        teacher.refresh_from_db()

        assert teacher.firstname == expected_firstname
        assert teacher.surname == expected_surname
        assert teacher.title == expected_title


@pytest.mark.django_db
class TestTeacherQueries:
    def test_get_lessons_per_week(self):
        """
        Test that the correct number of lessons per week is retrieved for a teacher.
        """
        # Make a lesson (& teacher)
        lesson = data_factories.Lesson()
        teacher = lesson.teacher

        # Execute test unit
        n_lessons = teacher.get_lessons_per_week()

        # Since this is the teacher's only lesson, they should just have the factory lesson to teach
        assert n_lessons == lesson.total_required_slots
