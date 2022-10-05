"""Unit tests for the TimetableSolverOutcome class"""

# Django imports
from django import test

# Local application imports
from data import models
from domain import solver as slvr


class TestTimetableSolverInputsLoading(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "unsolved_classes.json"]

    def test_add_slots_to_existing_fixed_class(self):
        """Test for the method adding timeslots to an existing fixed class"""
        # Test parameters
        time_slots = models.TimetableSlot.objects.get_specific_timeslots(school_id=123456, slot_ids=[3, 4])
        fixed_class = models.FixedClass.objects.get_individual_fixed_class(school_id=123456,
                                                                           class_id="YEAR_ONE_MATHS_A")

        # Execute test unit
        slvr.TimetableSolverOutcome._add_slots_to_existing_fixed_class(fixed_class=fixed_class, timeslots=time_slots)

        # Check outcome
        assert set(time_slots).issubset(fixed_class.time_slots.all())

    def test_create_new_fixed_class_from_time_slots(self):
        """Test for the method adding timeslots to an existing fixed class"""
        # Test parameters
        time_slots = models.TimetableSlot.objects.get_specific_timeslots(school_id=123456, slot_ids=[3, 4])
        unsolved_class = models.UnsolvedClass.objects.get_individual_unsolved_class(school_id=123456,
                                                                                    class_id="YEAR_ONE_MATHS_A")
        fixed_class = models.FixedClass.objects.get_individual_fixed_class(school_id=123456,
                                                                           class_id="YEAR_ONE_MATHS_A")
        fixed_class.delete()  # We make this class available for creation

        # Execute test unit
        slvr.TimetableSolverOutcome._create_new_fixed_class_from_time_slots(
            unsolved_class=unsolved_class, timeslots=time_slots)

        # Check outcome
        fixed_class = models.FixedClass.objects.get_individual_fixed_class(school_id=123456,
                                                                           class_id="YEAR_ONE_MATHS_A")
        self.assertQuerysetEqual(time_slots, fixed_class.time_slots.all(), ordered=False)
