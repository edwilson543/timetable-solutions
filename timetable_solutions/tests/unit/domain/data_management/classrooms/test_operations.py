"""Unit tests for teacher operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.classrooms import exceptions, operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewClassroom:
    def test_create_new_valid_classroom(self):
        # Make a school for the classroom
        school = data_factories.School()

        # Create the classroom
        classroom = operations.create_new_classroom(
            school_id=school.school_access_key,
            classroom_id=1,
            building="Test",
            room_number=1,
        )

        # Check the classroom now exists in db
        all_classrooms = models.Classroom.objects.all()
        assert all_classrooms.count() == 1
        assert all_classrooms.first() == classroom

    def test_raises_when_classroom_id_not_unique_for_school(self):
        classroom = data_factories.Classroom()

        with pytest.raises(exceptions.CouldNotCreateClassroom):
            operations.create_new_classroom(
                school_id=classroom.school.school_access_key,
                classroom_id=classroom.classroom_id,
                building="Test",
                room_number=33,
            )
