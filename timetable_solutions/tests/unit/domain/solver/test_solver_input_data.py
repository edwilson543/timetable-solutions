"""Test for the TimetableSolverInputs class """

# Standard library imports
from copy import deepcopy
import datetime as dt

# Django imports
from django import test

# Local application imports
from data import models
from domain import solver as slvr


class TestTimetableSolverInputsLoading(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "lessons_without_solution.json"]

    solution_spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                               allow_triple_periods_and_above=True)

    def test_instantiation_of_timetable_solver_inputs(self):
        """
        Test the solver data loader retrieves all data from the 'data' layer as expected
        """
        # Execute test unit
        data = slvr.TimetableSolverInputs(school_id=123456, solution_specification=self.solution_spec)

        # Check the outcome is as expected
        assert len(data.pupils) == 6
        assert len(data.teachers) == 11
        assert len(data.classrooms) == 12
        assert len(data.timetable_slots) == 35
        assert len(data.lessons) == 12  # Since the 12 lunch 'lessons' aren't included in the solver input data

    # PROPERTIES TESTS
    def test_consecutive_slots_property(self):
        """
        Test that the correct list of consecutive slots is returned by the consecutive_slots property method
        on the TimetableSolverInputs class.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        consecutive_slots = data.consecutive_slots

        # Check outcome
        assert len(consecutive_slots) == 30  # 7 slots per day, 5 days a week...
        # All timeslots are 1 hour apart, so we check this
        for double_slot in consecutive_slots:
            slot_0_start = dt.datetime.combine(dt.date(year=2020, month=1, day=1), time=double_slot[0].period_starts_at)
            slot_1_start = dt.datetime.combine(dt.date(year=2020, month=1, day=1), time=double_slot[1].period_starts_at)
            assert slot_0_start + dt.timedelta(hours=1) == slot_1_start
            assert double_slot[0].day_of_week == double_slot[1].day_of_week

    def test_available_days_property(self):
        """
        Test that the correct list of days, of the correct type, is returned by the available_days property method
        on the TimetableSolverInputs class.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        available_days = data.available_days

        # Check outcome
        assert available_days == [1, 2, 3, 4, 5]  # Represents Monday - Friday

    def test_user_defined_double_period_counts_property_one_double(self):
        """
        Test that the correct dictionary & structure is returned when trying to count the number of double periods
        within the user defined data.
        User defined data is filtered out, so we modify to ensure the double in the fixture gets found.
        """
        # Set test parameters
        lesson = models.Lesson.objects.get_individual_lesson(school_id=123456, lesson_id="YEAR_ONE_MATHS_A")
        slots = models.TimetableSlot.objects.filter(slot_id__in=[1, 6])  # Queryset contains one double period
        lesson.user_defined_time_slots.add(*slots)  # Manually give a user defined double

        data = slvr.TimetableSolverInputs(school_id=123456, solution_specification=self.solution_spec)

        # Execute test unit
        double_period_counts = data.user_defined_double_period_counts

        # Check outcome
        assert double_period_counts == {("YEAR_ONE_MATHS_A", 1): 1}

    def test_user_defined_double_period_counts_property_no_doubles(self):
        """
        Test that we get an empty dictionary when no Lessons contain a user-defined double period.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        double_period_counts = data.user_defined_double_period_counts

        # Check outcome
        assert double_period_counts == {}

    def test_timetable_start_property(self):
        """
        Unit test that the timetable start and finish span is correctly calculated.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        timetable_start = data.timetable_start

        # Check outcome
        assert timetable_start == 9  # Corresponds to 9:00

    def test_timetable_finish_property(self):
        """
        Unit test that the timetable start and finish span is correctly calculated.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        timetable_start = data.timetable_finish

        # Check outcome
        assert timetable_start == 16  # Correspond to 16:00

    # QUERIES TESTS
    def test_get_time_period_starts_at_from_slot_id(self):
        """
        Test that the correct period start time is looked up from the slot id.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
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
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

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
            school_id=123456, lesson_id="TEST", subject_name="MATHS", teacher_id=1, classroom_id=1,
            total_required_slots=100, total_required_double_periods=1, pupils=pupils)

        # Execute test unit and check outcome
        data = slvr.TimetableSolverInputs(school_id=123456, solution_specification=spec)

        # Check outcome - note the checks get performed at instantiation
        assert len(data.error_messages) == 1
