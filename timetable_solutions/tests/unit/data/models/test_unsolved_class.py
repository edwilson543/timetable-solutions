"""
Unit tests for the UnsolvedClassQuerySet (custom manager of the UnsolvedClass model), as well as UnsolvedClass itself.
"""

# Third party imports
import pytest

# Django imports
from django import test
from django.core.exceptions import ValidationError

# Local application imports
from data import models


class TestUnsolvedClass(test.TestCase):
    """
    Unit tests for the UnsolvedClas model
    """
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "unsolved_classes.json"]

    # FACTORY METHOD TESTS
    def test_create_new_valid_unsolved_class(self):
        """
        Tests that we can create and save a UnsolvedClass via the create_new method
        """
        # Set test parameters
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)

        # Execute test unit
        usc = models.UnsolvedClass.create_new(
            school_id=123456, class_id="TEST-A", subject_name="TEST",
            pupils=all_pupils, total_slots=10, n_double_periods=3, teacher_id=1, classroom_id=1)

        # Check outcome
        all_uscs = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        assert usc in all_uscs
        self.assertQuerysetEqual(all_pupils, usc.pupils.all(), ordered=False)

    def test_create_new_fails_when_pupil_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two UnsolvedClasses with the same id / school,
        due to unique_together on the Meta class
        """
        # Execute test unit
        with pytest.raises(ValidationError):
            models.UnsolvedClass.create_new(
                school_id=123456, class_id="YEAR_ONE_MATHS_A", subject_name="TEST",  # Note class id taken for school
                pupils=None, total_slots=10, n_double_periods=3, teacher_id=1, classroom_id=1)

    def test_create_new_fails_when_double_periods_invalid_for_total_periods(self):
        """
        Tests that we can cannot create two UnsolvedClasses with the same id / school,
        due to unique_together on the Meta class
        """
        # Set test parameters
        total_slots = 1
        n_double_periods = 1  # Clearly this isn't legit

        # Execute test unit
        with pytest.raises(ValidationError):
            models.UnsolvedClass.create_new(
                total_slots=total_slots, n_double_periods=n_double_periods,
                school_id=123456, class_id="UNIQUE-TEST", subject_name="TEST",
                pupils=None, teacher_id=1, classroom_id=1)
