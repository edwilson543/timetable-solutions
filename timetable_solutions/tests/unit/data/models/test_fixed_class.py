"""
Unit tests for the FixedClassQuerySet (custom manager of the FixedClass model), as well as FixedClass itself.
"""

# Django imports
from django import test

# Local application imports
from data import models


class TestFixedClass(test.TestCase):
    """Unit tests for the FixedClass model's custom queryset manager"""
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json"]

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
