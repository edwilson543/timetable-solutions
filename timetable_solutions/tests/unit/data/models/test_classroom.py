"""
Unit tests for methods on the Classroom class
"""

# Third party imports
import pytest

# Django imports
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import constants, models
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewClassroom:
    def test_create_new_valid_classroom(self):
        """
        Tests that we can create and save a Classroom via the create_new method
        """
        # Make a school for the classroom
        school = data_factories.School()

        # Create the classroom
        classroom = models.Classroom.create_new(
            school_id=school.school_access_key,
            classroom_id=1,
            building="Test",
            room_number=1,
        )

        # Check the classroom now exists in db
        all_classrooms = models.Classroom.objects.all()
        assert all_classrooms.count() == 1
        assert all_classrooms.first() == classroom

    def test_create_new_fails_when_classroom_id_not_unique_for_school(self):
        classroom = data_factories.Classroom()

        with pytest.raises(IntegrityError):
            models.Classroom.create_new(
                school_id=classroom.school.school_access_key,
                classroom_id=classroom.classroom_id,
                building="Test",
                room_number=33,
            )

    def test_create_new_fails_when_building_and_room_number_not_unique_for_school(self):
        classroom = data_factories.Classroom()

        with pytest.raises(IntegrityError):
            models.Classroom.create_new(
                school_id=classroom.school.school_access_key,
                classroom_id=classroom.classroom_id + 1,  # + 1 so that will be unique
                building=classroom.building,
                room_number=classroom.room_number,
            )


@pytest.mark.django_db
class TestUpdate:
    @pytest.mark.parametrize("building", ["English", None])
    @pytest.mark.parametrize("room_number", [100, None])
    def test_update_updates_teacher_details_with_params(
        self, building: str | None, room_number: int | None
    ):
        classroom = data_factories.Classroom()

        classroom.update(building=building, room_number=room_number)

        expected_building = building or classroom.building
        expected_room_number = room_number or classroom.room_number

        classroom.refresh_from_db()

        assert classroom.building == expected_building
        assert classroom.room_number == expected_room_number


@pytest.mark.django_db
class TestDeleteAllInstancesForSchool:
    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all classrooms associated with a school, when there are no Lesson
        instances referencing the classrooms as foreign keys.
        """
        # Get a classroom
        classroom = data_factories.Classroom()

        # Delete all the classrooms at our new classroom's school
        outcome = models.Classroom.delete_all_instances_for_school(
            school_id=classroom.school.school_access_key
        )

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.Classroom"] == 1

        all_classrooms = models.Classroom.objects.all()
        assert all_classrooms.count() == 0

    def test_delete_all_instances_for_school_unsuccessful_when_attached_to_lesson(self):
        """
        Test that we cannot delete all classrooms associated with a school, when there is at least one Lesson
        referencing the classrooms we are trying to delete.
        """
        # Make a lesson, with a classroom
        lesson = data_factories.Lesson()
        classroom = lesson.classroom

        # Check cannot delete classrooms
        with pytest.raises(ProtectedError):
            models.Classroom.delete_all_instances_for_school(
                school_id=classroom.school.school_access_key
            )

        # Check classroom still exists
        assert classroom in models.Classroom.objects.all()


@pytest.mark.django_db
class TestClassroomQueries:
    def test_get_lessons_per_week(self):
        """
        Test that the correct number of lessons per week is retrieved for a classroom.
        """
        # Get a lesson & classroom
        lesson = data_factories.Lesson()
        classroom = lesson.classroom

        # Execute test unit
        n_lessons = classroom.get_lessons_per_week()

        # Since this is the classroom's only lesson, it should just have the factory lesson to serve
        assert n_lessons == lesson.total_required_slots
