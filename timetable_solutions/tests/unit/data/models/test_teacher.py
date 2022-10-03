"""
Unit tests for methods on the Pupil class
"""
# Django imports
from django import test

# Local application imports
from data import models


class TestTeacher(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

    def test_check_if_busy_at_time_slot_when_teacher_is_busy(self):
        """Test that the check_if_busy_at_time_slot method returns 'True' when we expect it to"""
        teacher = models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=1)
        slot = models.TimetableSlot.objects.get_individual_timeslot(school_id=123456, slot_id=1)

        is_busy = teacher.check_if_busy_at_time_slot(slot=slot)
        assert is_busy

    def test_check_if_busy_at_time_slot_when_teacher_is_not_busy(self):
        """Test that the check_if_busy_at_time_slot method returns 'False' when we expect it to"""
        teacher = models.Teacher.objects.get_individual_teacher(school_id=123456, teacher_id=1)
        slot = models.TimetableSlot.objects.get_individual_timeslot(school_id=123456, slot_id=5)

        is_busy = teacher.check_if_busy_at_time_slot(slot=slot)
        assert not is_busy
