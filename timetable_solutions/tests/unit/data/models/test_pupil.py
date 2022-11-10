"""
Unit tests for methods on the Pupil class
"""

# Third party imports
import pytest

# Django imports
from django import test
from django.db import IntegrityError

# Local application imports
from data import models


class TestPupil(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

    # FACTORY METHOD TESTS
    def test_create_new_valid_pupil(self):
        """
        Tests that we can create and save a Pupil via the create_new method
        """
        # Execute test unit
        pupil = models.Pupil.create_new(school_id=123456, pupil_id=7, firstname="test", surname="test", year_group=1)

        # Check outcome
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        assert pupil in all_pupils

    def test_create_new_fails_when_pupil_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Pupils with the same id / school, due to unique_together on the Meta class
        """
        # Execute test unit
        with pytest.raises(IntegrityError):
            models.Pupil.create_new(school_id=123456, pupil_id=1,  # Note the pupil_id 1 is already taken
                                    firstname="test", surname="test", year_group=1)

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all pupils associated with a school
        """
        # Execute test unit
        outcome = models.Pupil.delete_all_instances_for_school(school_id=123456)

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.Pupil"] == 6
        assert deleted_ref["data.FixedClass_pupils"] == 18

        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        assert all_pupils.count() == 0

    # FILTER METHOD TESTS
    def test_check_if_busy_at_time_slot_when_pupil_is_busy(self):
        """
        Test that the check_if_busy_at_time_slot method returns 'True' when we expect it to
        """
        pup = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)
        slot = models.TimetableSlot.objects.get_individual_timeslot(school_id=123456, slot_id=1)

        is_busy = pup.check_if_busy_at_time_slot(slot=slot)
        assert is_busy

    def test_check_if_busy_at_time_slot_when_pupil_is_not_busy(self):
        """
        Test that the check_if_busy_at_time_slot method returns 'False' when we expect it to
        """
        pup = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)
        slot = models.TimetableSlot.objects.get_individual_timeslot(school_id=123456, slot_id=5)

        is_busy = pup.check_if_busy_at_time_slot(slot=slot)
        assert not is_busy
