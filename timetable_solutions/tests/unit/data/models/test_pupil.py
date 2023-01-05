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

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    # FACTORY METHOD TESTS
    def test_create_new_valid_pupil(self):
        """
        Tests that we can create and save a Pupil via the create_new method
        """
        # Execute test unit
        pupil = models.Pupil.create_new(
            school_id=123456,
            pupil_id=7,
            firstname="test",
            surname="test",
            year_group="1",
        )

        # Check outcome
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        assert pupil in all_pupils

        yg = models.YearGroup.objects.get_individual_year_group(
            school_id=123456, year_group="1"
        )
        assert pupil.year_group == yg

    def test_create_new_fails_when_pupil_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Pupils with the same id / school, due to unique_together on the Meta class
        """
        # Execute test unit
        with pytest.raises(IntegrityError):
            models.Pupil.create_new(
                school_id=123456,
                pupil_id=1,  # Note the pupil_id 1 is already taken
                firstname="test",
                surname="test",
                year_group="1",
            )

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all pupils associated with a school
        """
        # Execute test unit
        outcome = models.Pupil.delete_all_instances_for_school(school_id=123456)

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.Pupil"] == 6
        assert deleted_ref["data.Lesson_pupils"] == 24

        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        assert all_pupils.count() == 0

    # FILTER METHOD TESTS
    def test_check_if_busy_at_time_slot_when_pupil_is_busy(self):
        """
        Test that the check_if_busy_at_time_slot method returns 'True' when we expect it to
        """
        # Set test parameters
        pup = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)
        slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=1
        )

        # We ensure they are busy at this time
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        lesson.add_pupils(pupils=pup)
        lesson.add_user_defined_time_slots(time_slots=slot)

        # Execute test unit
        is_busy = pup.check_if_busy_at_time_slot(slot=slot)

        # Check outcome
        assert is_busy

    def test_check_if_busy_at_time_slot_when_pupil_is_not_busy(self):
        """
        Test that the check_if_busy_at_time_slot method returns 'False' when we expect it to
        """
        # Set test parameters
        pup = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)
        slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=5
        )

        # Execute test unit
        is_busy = pup.check_if_busy_at_time_slot(slot=slot)

        # Check outcome
        assert not is_busy

    # QUERY METHOD TESTS
    def test_get_lessons_per_week(self):
        """
        Test that the correct number of lessons per week is retrieved for a pupil.
        """
        # Set test parameters
        pupil = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)

        # Execute test unit
        weekly_lessons = pupil.get_lessons_per_week()

        # Check outcome
        assert weekly_lessons == 30

    def test_get_occupied_percentage(self):
        """
        Test that the correct occupied percentage is retrieved for a pupil.
        """
        # Set test parameters
        pupil = models.Pupil.objects.get_individual_pupil(school_id=123456, pupil_id=1)

        # Execute test unit
        percentage = pupil.get_occupied_percentage()

        # Check outcome
        assert percentage == (30 / 35)
