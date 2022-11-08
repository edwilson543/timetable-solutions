"""
Unit tests for methods on the Teacher class
"""

# Third party imports
import pytest

# Django imports
from django import test
from django.core.exceptions import ValidationError

# Local application imports
from data import models


class TestTeacher(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

    # FACTORY METHOD TESTS
    def test_create_new_valid_teacher(self):
        """
        Tests that we can create and save a Teacher via the create_new method
        """
        # Execute test unit
        teacher = models.Teacher.create_new(school_id=123456, teacher_id=12,  # Note that id 12 is available
                                            firstname="test", surname="test", title="mr")

        # Check outcome
        all_teachers = models.Teacher.objects.get_all_instances_for_school(school_id=123456)
        assert teacher in all_teachers

    def test_create_new_fails_when_teacher_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Teachers with the same id / school, due to unique_together on the Meta class
        """
        # Execute test unit
        with pytest.raises(ValidationError):
            models.Teacher.create_new(school_id=123456, teacher_id=1,  # Note that id 1 is unavailable
                                      firstname="test", surname="test", title="mr")

    # FILTER METHODS TESTS
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
