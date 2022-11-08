"""
Unit tests for methods on the Pupil class
"""

# Third party imports
import pytest

# Django imports
from django import test
from django.core.exceptions import ValidationError

# Local application imports
from data import models


class TestClassroom(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

    # FACTORY METHOD TESTS
    def test_create_new_valid_classroom(self):
        """
        Tests that we can create and save a Classroom via the create_new method
        """
        # Execute test unit
        classroom = models.Classroom.create_new(school_id=123456, classroom_id=100, building="Test", room_number=1)

        # Check outcome
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(school_id=123456)
        assert classroom in all_classrooms

    def test_create_new_fails_when_classroom_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Classrooms with the same id / school, due to unique_together on the
        Meta class
        """
        # Execute test unit
        with pytest.raises(ValidationError):
            models.Classroom.create_new(school_id=123456, classroom_id=1,  # Note that id 1 is already taken
                                        building="Test", room_number=1)

    def test_create_new_fails_when_building_and_roomnumber_not_unique_for_school(self):
        """
        Tests that we can cannot create two Classrooms with the same id / school, due to unique_together on the
        Meta class
        """
        # Execute test unit
        with pytest.raises(ValidationError):
            models.Classroom.create_new(school_id=123456, classroom_id=100,  # Note that id 100 is available
                                        building="MB", room_number=47)  #  MB 47 however is not available

    # FILTER METHODS TESTS
    def test_check_if_occupied_at_time_slot_classroom_occupied(self):
        """Test that the check_if_occupied_at_timeslot method returns 'True' when we expect it to"""
        classroom = models.Classroom.objects.get_individual_classroom(school_id=123456, classroom_id=1)
        slot = models.TimetableSlot.objects.get_individual_timeslot(school_id=123456, slot_id=1)

        is_occupied = classroom.check_if_occupied_at_time_slot(slot=slot)
        assert is_occupied

    def test_check_if_busy_at_time_slot_when_pupil_is_not_busy(self):
        """Test that the check_if_occupied_at_timeslot method returns 'False' when we expect it to"""
        classroom = models.Classroom.objects.get_individual_classroom(school_id=123456, classroom_id=1)
        slot = models.TimetableSlot.objects.get_individual_timeslot(school_id=123456, slot_id=5)

        is_occupied = classroom.check_if_occupied_at_time_slot(slot=slot)
        assert not is_occupied
