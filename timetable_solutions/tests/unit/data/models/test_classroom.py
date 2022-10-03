"""
Unit tests for methods on the Pupil class
"""
# Django imports
from django import test

# Local application imports
from data import models


class TestClassroom(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

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
