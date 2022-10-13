"""Test for the TimetableSolverInputs class """

# Standard library imports
import datetime as dt

# Django imports
from django import test

# Local application imports
from data import models
from domain import solver as slvr


class TestTimetableSolverInputsLoading(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes.json", "unsolved_classes.json"]

    def test_instantiation_of_timetable_solver(self):
        """
        Test the solver data loader retrieves all data from the 'data' layer as expected
        """
        # Set test parameters
        school_access_key = 123456
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True)

        # Execute test unit
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)

        # Check the outcome is as expected
        assert len(data.fixed_classes) == 12
        for fc in data.fixed_classes:
            assert isinstance(fc, models.FixedClass)

        assert len(data.unsolved_classes) == 12
        for uc in data.unsolved_classes:
            assert isinstance(uc, models.UnsolvedClass)

        assert len(data.timetable_slots) == 35
        for tts in data.timetable_slots:
            assert isinstance(tts, models.TimetableSlot)

        assert len(data.teachers) == 11
        for teacher in data.teachers:
            assert isinstance(teacher, models.Teacher)

        assert len(data.pupils) == 6
        for pupil in data.pupils:
            assert isinstance(pupil, models.Pupil)

        assert len(data.consecutive_slots) == 30  # 7 slots per day, 5 days a week...
        # All timeslots are 1 hour apart, so we check this
        for double_slot in data.consecutive_slots:
            slot_0_start = dt.datetime.combine(dt.date(year=2020, month=1, day=1), time=double_slot[0].period_starts_at)
            slot_1_start = dt.datetime.combine(dt.date(year=2020, month=1, day=1), time=double_slot[1].period_starts_at)
            assert slot_0_start + dt.timedelta(hours=1) == slot_1_start
            assert double_slot[0].day_of_week == double_slot[1].day_of_week
