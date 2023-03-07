"""
Unit tests for methods on the Classroom class
"""


# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import constants, models
from tests import data_factories as factories


@pytest.mark.django_db
class TestCreateNewClassroom:
    # --------------------
    # Factories tests
    # --------------------

    def test_create_new_valid_classroom(self):
        """
        Tests that we can create and save a Classroom via the create_new method
        """
        # Make a school for the classroom
        school = factories.School()

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
        classroom = factories.Classroom()

        with pytest.raises(IntegrityError):
            models.Classroom.create_new(
                school_id=classroom.school.school_access_key,
                classroom_id=classroom.classroom_id,
                building="Test",
                room_number=33,
            )

    def test_create_new_fails_when_building_and_room_number_not_unique_for_school(self):
        classroom = factories.Classroom()

        with pytest.raises(IntegrityError):
            models.Classroom.create_new(
                school_id=classroom.school.school_access_key,
                classroom_id=classroom.classroom_id + 1,  # + 1 so that will be unique
                building=classroom.building,
                room_number=classroom.room_number,
            )


@pytest.mark.django_db
class TestDeleteAllInstancesForSchool:
    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all classrooms associated with a school, when there are no Lesson
        instances referencing the classrooms as foreign keys.
        """
        # Get a classroom
        classroom = factories.Classroom()

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
        lesson = factories.Lesson()
        classroom = lesson.classroom

        # Check cannot delete classrooms
        with pytest.raises(ProtectedError):
            models.Classroom.delete_all_instances_for_school(
                school_id=classroom.school.school_access_key
            )

        # Check classroom still exists
        assert classroom in models.Classroom.objects.all()

    # --------------------
    # Queries tests
    # --------------------

    def test_check_if_occupied_at_time_of_timeslot_classroom_occupied_at_slot(self):
        """Test that the check_if_occupied_at_timeslot method returns 'True' when we expect it to"""
        # Make a classroom with a lesson fixed at some slot
        classroom = factories.Classroom()
        school = classroom.school
        slot = factories.TimetableSlot(school=school)
        factories.Lesson(
            school=school, classroom=classroom, user_defined_time_slots=(slot,)
        )

        # Call test function
        is_occupied = classroom.check_if_occupied_at_time_of_timeslot(slot=slot)

        # Check classroom successfully made busy
        assert is_occupied

    def test_check_if_occupied_at_time_of_timeslot_classroom_occupied_at_exact_times_of_slot(
        self,
    ):
        """Test that the check_if_occupied_at_timeslot method returns 'True' when we expect it to"""
        # Make a classroom with a lesson fixed at some slot
        classroom = factories.Classroom()
        school = classroom.school
        busy_slot = factories.TimetableSlot(school=school)
        factories.Lesson(
            school=school, classroom=classroom, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot with the exact same times (and day) to check business against
        check_slot = factories.TimetableSlot(
            school=school,
            day_of_week=busy_slot.day_of_week,
            starts_at=busy_slot.starts_at,
            ends_at=busy_slot.ends_at,
        )

        # Call test function
        is_occupied = classroom.check_if_occupied_at_time_of_timeslot(slot=check_slot)

        # Check classroom successfully made busy
        assert is_occupied

    def test_check_if_occupied_at_time_of_timeslot_partially_overlapping(self):
        """Test that a classroom is busy if it's in use during another slot with overlapiong times."""
        # Make a classroom with a lesson fixed at some slot
        classroom = factories.Classroom()
        school = classroom.school
        busy_slot = factories.TimetableSlot(
            school=school,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )
        factories.Lesson(
            school=school, classroom=classroom, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot with the exact same times (and day) to check business against
        check_slot = factories.TimetableSlot(
            school=school,
            day_of_week=busy_slot.day_of_week,
            starts_at=dt.time(hour=9, minute=30),
            ends_at=dt.time(hour=10, minute=30),
        )

        # Call test function
        is_occupied = classroom.check_if_occupied_at_time_of_timeslot(slot=check_slot)

        # Check classroom successfully made busy
        assert is_occupied

    def test_check_if_busy_at_time_slot_when_classroom_is_not_occupied(self):
        """Test that the check_if_occupied_at_timeslot method returns 'False' when we expect it to"""
        # Make a classroom with a lesson fixed at some slot
        # The business isn't really necessary, but ensures having one lesson doesn't
        # make the teacher constantly 'busy'
        classroom = factories.Classroom()
        school = classroom.school
        busy_slot = factories.TimetableSlot(
            school=school, day_of_week=constants.Day.MONDAY
        )
        factories.Lesson(
            school=school, classroom=classroom, user_defined_time_slots=(busy_slot,)
        )

        # Make another slot, which has a different day
        check_slot = factories.TimetableSlot(
            school=school, day_of_week=constants.Day.TUESDAY
        )

        # Call test function
        is_occupied = classroom.check_if_occupied_at_time_of_timeslot(slot=check_slot)

        # Check classroom unoccupied
        assert not is_occupied

    def test_get_lessons_per_week(self):
        """
        Test that the correct number of lessons per week is retrieved for a classroom.
        """
        # Get a lesson & classroom
        lesson = factories.Lesson()
        classroom = lesson.classroom

        # Execute test unit
        n_lessons = classroom.get_lessons_per_week()

        # Since this is the classroom's only lesson, it should just have the factory lesson to serve
        assert n_lessons == lesson.total_required_slots
