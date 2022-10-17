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

    solution_spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                               allow_triple_periods_and_above=True)

    def test_instantiation_of_timetable_solver_inputs(self):
        """
        Test the solver data loader retrieves all data from the 'data' layer as expected
        """
        # Execute test unit
        data = slvr.TimetableSolverInputs(school_id=123456, solution_specification=self.solution_spec)

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

    def test_fixed_class_double_period_counts_property_one_double(self):
        """
        Test that the correct dictionary & structure is returned when trying to count the number of double periods
        within the user defined data.
        User defined data is filtered out, so we modify to ensure the double in the fixture gets found.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        for fc in data.fixed_classes:
            fc.user_defined = True  # To avoid creating another fixture, we just mutate here

        # Execute test unit
        double_period_counts = data.fixed_class_double_period_counts

        # Check outcome
        assert double_period_counts == {("YEAR_ONE_MATHS_A", 1): 1}

    def test_fixed_class_double_period_counts_property_no_doubles(self):
        """
        Test that we get an empty dictionary when all FixedClass data is not user-defined
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        double_period_counts = data.fixed_class_double_period_counts

        # Check outcome
        assert double_period_counts == {}

    def test_timetable_start_finish_span_as_ints(self):
        """
        Unit test that the timetable start and finish span is correctly calculated.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        timetable_start_finish = data.timetable_start_finish_span_as_ints

        # Check outcome
        assert timetable_start_finish == (9, 16)  # 9:00 - 16:00

    # QUERIES TESTS
    def test_get_fixed_class_corresponding_to_unsolved_class_existent_id_returns_fixed_class(self):
        """
        Test that a Fixed Class is returned from an UnsolvedClass with a corresponding fixed class.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        fixed_class = data.get_fixed_class_corresponding_to_unsolved_class(unsolved_class_id="YEAR_ONE_MATHS_A")

        # Check outcome
        assert isinstance(fixed_class, models.FixedClass)

    def test_get_fixed_class_corresponding_to_unsolved_class_non_existent_id_returns_none(self):
        """
        Test that a None is returned from an UnsolvedClass without a corresponding fixed class.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)

        # Execute test unit
        fixed_class = data.get_fixed_class_corresponding_to_unsolved_class(unsolved_class_id="NON-EXISTENT")

        # Check outcome
        assert fixed_class is None

    def test_get_time_period_starts_at_from_slot_id(self):
        """
        Test that we get an empty dictionary when all FixedClass data is not user-defined
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        slot_id = 1

        # Execute test unit
        period_starts_at = data.get_time_period_starts_at_from_slot_id(slot_id=slot_id)

        # Check outcome
        assert period_starts_at == dt.time(hour=9)
