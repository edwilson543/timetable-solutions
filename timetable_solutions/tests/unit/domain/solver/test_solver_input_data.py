"""Test for the TimetableSolverInputs class """

# Standard library imports
from copy import deepcopy
import datetime as dt

# Django imports
from django import test
from django.core import management

# Local application imports
from data import models
from domain import solver as slvr


class TestTimetableSolverInputsLoading(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_without_solution.json",
    ]

    solution_spec = slvr.SolutionSpecification(
        allow_split_classes_within_each_day=True, allow_triple_periods_and_above=True
    )

    def test_instantiation_of_timetable_solver_inputs(self):
        """
        Test the solver data loader retrieves all data from the 'data' layer as expected
        """
        # Execute test unit
        data = slvr.TimetableSolverInputs(
            school_id=123456, solution_specification=self.solution_spec
        )

        # Check the outcome is as expected
        assert len(data.pupils) == 6
        assert len(data.teachers) == 11
        assert len(data.classrooms) == 12
        assert len(data.timetable_slots) == 35
        assert (
            len(data.lessons) == 12
        )  # Since the 12 lunch 'lessons' aren't included in the solver input data

    # Tests for properties / methods for objective function
    def test_timetable_start_as_float(self):
        """
        Unit test that the timetable start and finish span is correctly calculated.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )

        # Execute test unit
        timetable_start = data.timetable_start_hour_as_float

        # Check outcome
        assert timetable_start == 9  # Corresponds to 9:00

    def test_timetable_start_as_float_extra_year(self):
        """
        Unit test that the timetable start and finish span is correctly calculated,
        when different year groups have different timetables.
        """
        # Set test parameters
        management.call_command("loaddata", "extra-year.json")
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )

        # Execute test unit
        timetable_start = data.timetable_start_hour_as_float

        # Check outcome
        assert (
            timetable_start == 8.5
        )  # Corresponds to 8:30, the start time of the extra year

    def test_timetable_finish_as_float(self):
        """
        Unit test that the timetable start and finish span is correctly calculated.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )

        # Execute test unit
        timetable_start = data.timetable_finish_hour_as_float

        # Check outcome
        assert timetable_start == 16  # Corresponds to 16:00

    # Tests for methods for variables
    def test_get_consecutive_slots_for_year_group_one_timetable(self):
        """
        Test that the correct list of consecutive slots is returned for Year 1,
        when all year groups share a set of timetable slots.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )
        year_one = models.YearGroup.objects.get_individual_year_group(
            school_id=123456, year_group="1"
        )

        # Execute test unit
        consecutive_slots = data.get_consecutive_slots_for_year_group(
            year_group=year_one
        )

        # Check outcome
        assert len(consecutive_slots) == 30  # 7 slots per day, 5 days a week...
        # All timeslots are 1 hour apart, so we check this
        for double_slot in consecutive_slots:
            slot_0_start = dt.datetime.combine(
                dt.date(year=2020, month=1, day=1), time=double_slot[0].period_starts_at
            )
            slot_1_start = dt.datetime.combine(
                dt.date(year=2020, month=1, day=1), time=double_slot[1].period_starts_at
            )
            assert slot_0_start + dt.timedelta(hours=1) == slot_1_start
            assert double_slot[0].day_of_week == double_slot[1].day_of_week

    def test_get_consecutive_slots_for_year_group_varied_timetables(self):
        """
        Test that the correct list of consecutive slots is returned for Year 1,
        when some year groups have different timetable slots.
        """
        # Set test parameters
        management.call_command("loaddata", "extra-year.json")

        slot_0 = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456,
            slot_id=100,
        )
        slot_1 = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456,
            slot_id=101,
        )
        extra_year = models.YearGroup.objects.get_individual_year_group(
            school_id=123456, year_group="extra-year"
        )

        data = slvr.TimetableSolverInputs(
            school_id=123456, solution_specification=self.solution_spec
        )

        # Execute test unit
        consecutive_slots = data.get_consecutive_slots_for_year_group(
            year_group=extra_year
        )

        # Check outcome
        assert len(consecutive_slots) == 1  # We only created one candidate
        assert consecutive_slots[0][0] == slot_0
        assert consecutive_slots[0][1] == slot_1

    def test_get_time_period_starts_at_from_slot_id(self):
        """
        Test that the correct period start time is looked up from the slot id.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )
        slot_id = 1

        # Execute test unit
        period_starts_at = data.get_time_period_starts_at_from_slot_id(slot_id=slot_id)

        # Check outcome
        assert period_starts_at == dt.time(hour=9)

    # CHECKS TESTS
    def test_check_specification_aligns_with_input_data_no_issues(self):
        """
        Test that we retain an empty list of error messages after performing the checks, when there are no issues
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )

        # Check outcome - note the checks get performed at instantiation
        assert data.error_messages == []

    def test_check_specification_aligns_with_input_data_forced_issue(self):
        """
        Test that we get the expected error message when the solution spec and input data are not compatible.
        """
        # Set test parameters
        spec = deepcopy(self.solution_spec)

        # Create a source of incompatibility - a spec disallowing split classes, but requiring too many (100...)
        spec.allow_split_classes_within_each_day = False
        pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        models.Lesson.create_new(
            school_id=123456,
            lesson_id="TEST",
            subject_name="MATHS",
            teacher_id=1,
            classroom_id=1,
            total_required_slots=100,
            total_required_double_periods=1,
            pupils=pupils,
        )

        # Execute test unit and check outcome
        data = slvr.TimetableSolverInputs(school_id=123456, solution_specification=spec)

        # Check outcome - note the checks get performed at instantiation
        assert len(data.error_messages) == 1
