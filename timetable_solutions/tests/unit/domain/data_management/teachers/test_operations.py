"""Unit tests for teacher operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.teachers import exceptions, operations
from tests import data_factories as factories


@pytest.mark.django_db
class TestTeacher:

    # --------------------
    # Factories tests
    # --------------------

    def test_create_new_valid_teacher(self):
        """
        Tests that we can create and save a Teacher via the create_new method
        """
        # Make a school for the teacher to teach at
        school = factories.School()

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

    def test_create_new_fails_when_teacher_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Teachers with the same id / school, due to unique_together on the Meta class
        """
        # Make a teacher to occupy an id value
        teacher = factories.Teacher()

        # Try making a teacher with the same school / id
        with pytest.raises(exceptions.CouldNotCreateTeacher):
            operations.create_new_teacher(
                school_id=teacher.school.school_access_key,
                teacher_id=teacher.teacher_id,
                firstname="test-2",
                surname="test-2",
                title="mrs",
            )
