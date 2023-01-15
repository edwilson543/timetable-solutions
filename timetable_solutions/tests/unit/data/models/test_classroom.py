"""
Unit tests for methods on the Classroom class
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django import test
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import models


class TestClassroom(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "teachers.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    # FACTORY METHOD TESTS
    def test_create_new_valid_classroom(self):
        """
        Tests that we can create and save a Classroom via the create_new method
        """
        # Execute test unit
        classroom = models.Classroom.create_new(
            school_id=123456, classroom_id=100, building="Test", room_number=1
        )

        # Check outcome
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert classroom in all_classrooms

    def test_create_new_fails_when_classroom_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Classrooms with the same id / school, due to unique_together on the
        Meta class
        """
        # Execute test unit
        with pytest.raises(IntegrityError):
            models.Classroom.create_new(
                school_id=123456,
                classroom_id=1,  # Note that id 1 is already taken
                building="Test",
                room_number=1,
            )

    def test_create_new_fails_when_building_and_roomnumber_not_unique_for_school(self):
        """
        Tests that we can cannot create two Classrooms with the same id / school, due to unique_together on the
        Meta class
        """
        # Execute test unit
        with pytest.raises(IntegrityError):
            models.Classroom.create_new(
                school_id=123456,
                classroom_id=100,  # Note that id 100 is available
                building="MB",
                room_number=47,  # MB47 however is not available
            )

    def test_delete_all_instances_for_school_unsuccessful_when_attached_to_lesson(self):
        """
        Test that we cannot delete all classrooms associated with a school, when there is at least one Lesson
        referencing the classrooms we are trying to delete.
        """
        # Execute test unit
        with pytest.raises(ProtectedError):
            models.Classroom.delete_all_instances_for_school(school_id=123456)

    # QUERY METHODS TESTS
    def test_check_if_occupied_at_time_of_timeslot_classroom_occupied_at_slot(self):
        """Test that the check_if_occupied_at_timeslot method returns 'True' when we expect it to"""
        # Set test parameters
        classroom = models.Classroom.objects.get_individual_classroom(
            school_id=123456, classroom_id=1
        )
        slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=1
        )

        # We ensure they are busy at this time
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        lesson.classroom = classroom
        lesson.add_user_defined_time_slots(time_slots=slot)

        # Execute test unit
        is_occupied = classroom.check_if_occupied_at_time_of_timeslot(slot=slot)

        # Check outcome
        assert is_occupied

    def test_check_if_occupied_at_time_of_timeslot_classroom_occupied_at_exact_times_of_slot(
        self,
    ):
        """Test that the check_if_occupied_at_timeslot method returns 'True' when we expect it to"""
        # Set test parameters
        classroom = models.Classroom.objects.get_individual_classroom(
            school_id=123456, classroom_id=1
        )
        nine_to_ten = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=1
        )

        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        lesson.classroom = classroom
        lesson.add_user_defined_time_slots(time_slots=nine_to_ten)

        # Create a slot to check against
        another_nine_to_ten = models.TimetableSlot.create_new(
            school_id=123456,
            slot_id=1000,
            period_starts_at=dt.time(hour=9),
            period_ends_at=dt.time(hour=10),
            relevant_year_groups=None,
            day_of_week=models.WeekDay.MONDAY,
        )

        # Execute test unit
        is_occupied = classroom.check_if_occupied_at_time_of_timeslot(
            slot=another_nine_to_ten
        )

        # Check outcome
        assert is_occupied

    def test_check_if_occupied_at_time_of_timeslot_partially_overlapping(self):
        """Test that a classroom is busy if it's in use during another slot with overlapiong times."""
        # Set test parameters
        classroom = models.Classroom.objects.get_individual_classroom(
            school_id=123456, classroom_id=1
        )
        nine_to_ten = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=1
        )

        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        lesson.classroom = classroom
        lesson.add_user_defined_time_slots(time_slots=nine_to_ten)

        # Create a slot to check against
        eight_30_nine_30 = models.TimetableSlot.create_new(
            school_id=123456,
            slot_id=1000,
            period_starts_at=dt.time(hour=8, minute=30),
            period_ends_at=dt.time(hour=9, minute=30),
            relevant_year_groups=None,
            day_of_week=models.WeekDay.MONDAY,
        )

        # Execute test unit
        is_occupied = classroom.check_if_occupied_at_time_of_timeslot(
            slot=eight_30_nine_30
        )

        # Check outcome
        assert is_occupied

    def test_check_if_busy_at_time_slot_when_classroom_is_not_occupied(self):
        """Test that the check_if_occupied_at_timeslot method returns 'False' when we expect it to"""
        # Set test parameters
        classroom = models.Classroom.objects.get_individual_classroom(
            school_id=123456, classroom_id=1
        )
        slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=5
        )

        # Execute test unit
        is_occupied = classroom.check_if_occupied_at_time_of_timeslot(slot=slot)

        # Check outcome
        assert not is_occupied

    def test_get_lessons_per_week(self):
        """
        Test that the correct number of lessons per week is retrieved for a classroom.
        """
        # Set test parameters
        classroom = models.Classroom.objects.get_individual_classroom(
            school_id=123456, classroom_id=1
        )

        # Execute test unit
        n_lessons = classroom.get_lessons_per_week()

        # Check outcome
        assert n_lessons == 8


class TestClassroomLessFixtures(test.TestCase):
    """
    Test class only loading in the school / classroom fixtures, to avoid foreign key issues.
    """

    fixtures = ["user_school_profile.json", "classrooms.json"]

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all classrooms associated with a school, when there are no Lesson
        instances referencing the classrooms as foreign keys.
        """
        # Execute test unit
        outcome = models.Classroom.delete_all_instances_for_school(school_id=123456)

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.Classroom"] == 12

        all_classrooms = models.Classroom.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_classrooms.count() == 0
