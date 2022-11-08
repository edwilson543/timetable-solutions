"""
Unit tests for the FixedClassQuerySet (custom manager of the FixedClass model), as well as FixedClass itself.
"""

# Third party imports
import pytest

# Django imports
from django import test
from django.core.exceptions import ValidationError

# Local application imports
from data import models


class TestFixedClass(test.TestCase):
    """
    Unit tests for the FixedClass model
    """
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

    # FACTORY METHOD TESTS
    def test_create_new_valid_fixed_class(self):
        """
        Tests that we can create and save a FixedClass via the create_new method
        """
        # Set test parameters
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)

        # Execute test unit
        fc = models.FixedClass.create_new(school_id=123456, class_id="TEST-A", subject_name="TEST", user_defined=True,
                                          pupils=all_pupils, time_slots=all_slots, teacher_id=1, classroom_id=1)

        # Check outcome
        all_fcs = models.FixedClass.objects.get_all_instances_for_school(school_id=123456)
        assert fc in all_fcs
        self.assertQuerysetEqual(all_pupils, fc.pupils.all(), ordered=False)
        self.assertQuerysetEqual(all_slots, fc.time_slots.all(), ordered=False)

    def test_create_new_fails_when_pupil_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two FixedClasses with the same (class_id, school, user_defined) combination,
        due to unique_together on the Meta class
        """
        # Execute test unit
        with pytest.raises(ValidationError):
            models.FixedClass.create_new(
                school_id=123456, class_id="YEAR_ONE_MATHS_A", user_defined=False,  # This combo is already in fixture
                subject_name="TEST", pupils=None, time_slots=None, teacher_id=1, classroom_id=1)

    def test_delete_all_non_user_defined_fixed_classes(self):
        """
        Test that the behaviour when deleting the queryset of FixedClass instances is as expected, i.e. that nothing is
        getting deleted that shouldn't be.
        """
        # Set test parameters
        all_fc = models.FixedClass.objects.get_all_instances_for_school(school_id=123456)
        expected_pupil_ref_count = sum(fc.pupils.all().count() for fc in all_fc if not fc.user_defined)
        expected_tt_slot_ref_count = sum(fc.time_slots.all().count() for fc in all_fc if not fc.user_defined)

        # Execute test unit
        info = models.FixedClass.delete_all_non_user_defined_fixed_classes(school_id=123456, return_info=True)

        # Check outcome - that the correct instances and references have been deleted
        deleted = info[1]
        assert deleted["data.FixedClass"] == 12
        assert deleted["data.FixedClass_pupils"] == expected_pupil_ref_count == 18  # Average 1.5 pups / class
        assert deleted["data.FixedClass_time_slots"] == expected_tt_slot_ref_count == 100  # Average 8.33 slots / class

        # Check outcome - that nothing that shouldn't have been deleted has been
        assert models.Pupil.objects.get_all_instances_for_school(school_id=123456).count() == 6
        assert models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456).count() == 35
        assert models.Teacher.objects.get_all_instances_for_school(school_id=123456).count() == 11
        assert models.Classroom.objects.get_all_instances_for_school(school_id=123456).count() == 12

    # QUERY METHOD TESTS
    def test_get_double_period_count_on_day_raises(self):
        """Unit test to check that we are disallowed from counting the double periods on a non-user defined FC."""
        # Set test parameters
        fixed_class = models.FixedClass.objects.get_individual_fixed_class(
            school_id=123456, class_id="YEAR_ONE_MATHS_A")

        # Execute test unit
        with pytest.raises(ValueError):
            fixed_class.get_double_period_count_on_day(day_of_week=models.WeekDay.MONDAY.value)

    def test_get_double_period_count_on_day_one_double_expected(self):
        """
        Unit test that the method for counting the number of double periods a given FixedClass correctly identifies that
        there is one FixedClass double period on Monday, for the YEAR_ONE_MATHS_A group.
        """
        # Set test parameters
        fixed_class = models.FixedClass.objects.get_individual_fixed_class(
            school_id=123456, class_id="YEAR_ONE_MATHS_A")
        fixed_class.user_defined = True  # To avoid creating another fixture, we just mutate here
        day_of_week = models.WeekDay.MONDAY.value

        # Execute test unit
        double_period_count = fixed_class.get_double_period_count_on_day(day_of_week=day_of_week)

        # Check outcome
        assert double_period_count == 1

    def test_get_double_period_count_on_day_no_doubles_expected(self):
        """
        Unit test that the method for counting the number of double periods a given FixedClass correctly identifies that
        there are NOT ANY FixedClass double period on Tuesday, for the YEAR_ONE_MATHS_A group.
        """
        # Set test parameters
        fixed_class = models.FixedClass.objects.get_individual_fixed_class(
            school_id=123456, class_id="YEAR_ONE_MATHS_A")
        fixed_class.user_defined = True  # To avoid creating another fixture, we just mutate here
        day_of_week = models.WeekDay.TUESDAY.value

        # Execute test unit
        double_period_count = fixed_class.get_double_period_count_on_day(day_of_week=day_of_week)

        # Check outcome
        assert double_period_count == 0
