"""Unit tests for classroom operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.classrooms import operations
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

        with pytest.raises(operations.UnableToCreateClassroom) as exc:
            operations.create_new_classroom(
                school_id=classroom.school.school_access_key,
                classroom_id=classroom.classroom_id,
                building="Test",
                room_number=33,
            )

        assert (
            f"Classroom with this data already exists."
            in exc.value.human_error_message
            in str(exc.value.human_error_message)
        )

    def test_raises_when_classroom_building_room_number_combination_not_unique_for_school(
        self,
    ):
        classroom = data_factories.Classroom()

        with pytest.raises(operations.UnableToCreateClassroom) as exc:
            operations.create_new_classroom(
                school_id=classroom.school.school_access_key,
                classroom_id=classroom.classroom_id + 1,
                building=classroom.building,
                room_number=classroom.room_number,
            )

        assert (
            f"Classroom with this data already exists." in exc.value.human_error_message
        )


@pytest.mark.django_db
class TestUpdatedClassroom:
    def test_updated_classroom_updates_details_in_db(self):
        classroom = data_factories.Classroom()

        # Create the classroom
        operations.update_classroom(classroom, building="Science", room_number=100)

        # Check the classroom was updated
        classroom.refresh_from_db()
        assert classroom.building == "Science"
        assert classroom.room_number == 100


@pytest.mark.django_db
class TestDeleteClassroom:
    def test_can_delete_unprotected_classroom(self):
        classroom = data_factories.Classroom()

        # Create the classroom
        operations.delete_classroom(classroom)

        # Check the classroom was deleted
        with pytest.raises(models.Classroom.DoesNotExist):
            classroom.refresh_from_db()

    def test_raises_when_classroom_protected(self):
        # Note the lesson -> classroom foreign key is protected
        lesson = data_factories.Lesson()

        with pytest.raises(operations.UnableToDeleteClassroom) as exc:
            operations.delete_classroom(lesson.classroom)

        assert "at least one lesson" in exc.value.human_error_message
