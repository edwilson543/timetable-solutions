"""Test for the TimetableSolverInputs class."""

# Standard library imports
import datetime as dt
import random

# Third party imports
import pytest


# Local application imports
from data import constants as data_constants
from data import models
from domain import solver as slvr
from tests import data_factories
from tests import domain_factories


def make_and_get_school_data(
    school: models.School = None,
    pupils: list[models.Pupil] = None,
    slots: list[models.TimetableSlot] = None,
    lessons: list[models.Lesson] = None,
) -> tuple[
    models.School,
    list[models.Pupil],
    list[models.TimetableSlot],
    list[models.Lesson],
]:
    """Make & get a set of database level input data for a school."""
    if not school:
        school = data_factories.School()
    # We make a random number of pupils / slots / lessons
    # Note this doesn't give a solvable problem, only some testable input data
    if not pupils:
        pupils = [
            data_factories.Pupil(school=school) for _ in range(0, random.randint(1, 10))
        ]
    if not slots:
        slots = [
            data_factories.TimetableSlot(school=school)
            for _ in range(0, random.randint(1, 10))
        ]
    if not lessons:
        lessons = [
            data_factories.Lesson(school=school)
            for _ in range(0, random.randint(1, 10))
        ]
    return school, pupils, slots, lessons


@pytest.mark.django_db
class TestTimetableSolverInputsLoading:
    def test_instantiation_of_timetable_solver_inputs(self):
        """
        Test the solver data loader retrieves all data from the 'data' layer as expected
        """
        # Get and make some data
        school, pupils, slots, lessons = make_and_get_school_data()

        # Make some data that shouldn't be included in the inputs
        make_and_get_school_data()

        # Gather all this input data
        spec = domain_factories.SolutionSpecification()
        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key, solution_specification=spec
        )

        # Check all factory data was retrieved, and only the relevant portion
        assert data.school_id == school.school_access_key
        assert data.solution_specification == spec
        assert len(data.pupils) == len(pupils)
        assert len(data.timetable_slots) == len(slots)
        assert len(data.lessons) == len(lessons)

        # One teacher / classroom is created per lesson from subfactories
        assert len(data.teachers) == len(lessons)
        assert len(data.classrooms) == len(lessons)

        assert len(data.error_messages) == 0


@pytest.mark.django_db
class TestTimetableSolverInputsHelperMethods:
    def test_timetable_start_as_float_matches_lone_slots_start_time(self):
        # Get and make some data
        school = data_factories.School()
        slot = data_factories.TimetableSlot(
            school=school, starts_at=dt.time(hour=8, minute=15)
        )
        later_slot = data_factories.TimetableSlot(
            school=school, starts_at=dt.time(hour=9, minute=13)
        )
        make_and_get_school_data(school=school, slots=[slot, later_slot])

        # Get the input data & timetable start time
        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )
        timetable_start = data.timetable_start_hour_as_float

        # Check timetable starts at time of the earliest slot (08:15)
        assert timetable_start == 8.25

    def test_timetable_finish_as_float_matches_lone_slots_end_time(self):
        # Get and make some data
        school = data_factories.School()
        slot = data_factories.TimetableSlot(
            school=school, ends_at=dt.time(hour=16, minute=48)
        )
        earlier_slot = data_factories.TimetableSlot(
            school=school, ends_at=dt.time(hour=16, minute=47)
        )
        make_and_get_school_data(school=school, slots=[slot, earlier_slot])

        # Get the input data & timetable start time
        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )
        timetable_finish = data.timetable_finish_hour_as_float

        # Check timetable ends at time of the latest slot (16:48)
        assert timetable_finish == 16.8

    # --------------------
    # Tests for helper methods for TimetableSolverVariables
    # --------------------

    def test_get_consecutive_slots_for_year_group_when_one_pair_of_consecutive_slots(
        self,
    ):
        # Get and make some data, which includes 2 slots which are consecutive
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        slot_0 = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))
        slot_1 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)
        make_and_get_school_data(school=school, slots=[slot_0, slot_1])

        # Gather the input data object
        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Get the slots for our factory-produce year group
        consecutive_slots = data.get_consecutive_slots_for_year_group(year_group=yg)

        # Check outcome
        assert consecutive_slots == [(slot_0, slot_1)]

    def test_get_consecutive_slots_for_year_group_when_no_consecutive_slots(self):
        # Get and make some data, which includes no consecutive slots
        school = data_factories.School()
        yg_0 = data_factories.YearGroup(school=school)
        slot_0 = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg_0,),
            starts_at=dt.time(hour=9),
        )

        # Make a slot for this year group but not a consecutive one
        slot_1 = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg_0,),
            starts_at=dt.time(hour=16),
        )

        # Make a slot consecutive to slot_0, but for a different year group
        yg_1 = data_factories.YearGroup(school=school)
        slot_2 = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg_1,),
            starts_at=slot_0.ends_at,
            day_of_week=slot_0.day_of_week,
        )

        make_and_get_school_data(school=school, slots=[slot_0, slot_1, slot_2])

        # Gather the input data object
        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        for yg_0 in [yg_0, yg_1]:
            # Get the slots for each year group, and check none appear consecutive
            consecutive_slots = data.get_consecutive_slots_for_year_group(
                year_group=yg_0
            )
            assert consecutive_slots == []

    def test_get_time_starts_at_from_slot_id_equals_slot_start_time(self):
        # Get and make some data
        school, _, slots, _ = make_and_get_school_data()

        data = slvr.TimetableSolverInputs(
            school_id=school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )
        slot = slots[0]

        # Execute test unit
        starts_at = data.get_time_starts_at_from_slot_id(slot_id=slot.slot_id)

        # Check outcome
        assert starts_at == slot.starts_at


@pytest.mark.django_db
class TestTimetableSolverInputsValidation:
    def test_error_when_lesson_requires_too_many_days_and_disallows_split_classes(self):
        # Make a lesson requiring more slots than there are days of the week
        days_of_week = len(data_constants.Day)
        lesson = data_factories.Lesson.with_n_pupils(
            total_required_slots=days_of_week + 1, total_required_double_periods=0
        )
        yg = lesson.pupils.first().year_group
        # Create a slot for each day of the week, which our lesson could utilise
        for day in data_constants.Day:
            data_factories.TimetableSlot(
                school=lesson.school, relevant_year_groups=(yg,), day_of_week=day
            )

        # Make a spec disallowing split classes within a day, and gather the input data
        spec = domain_factories.SolutionSpecification(
            allow_split_classes_within_each_day=False
        )
        data = slvr.TimetableSolverInputs(
            school_id=lesson.school.school_access_key, solution_specification=spec
        )

        # Check outcome - note the checks get performed at instantiation
        assert len(data.error_messages) == 1
        error = data.error_messages[0]
        assert f"{lesson} requires too many distinct slots for the solution" in error

    def test_error_when_lesson_has_solver_define_solution(self):
        # Make a lesson with a solver defined slot
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)
        lesson = data_factories.Lesson.with_n_pupils(
            school=school,
            solver_defined_time_slots=(slot,),
            total_required_slots=2,
            total_required_double_periods=0,
        )

        # Get and validate the input data
        data = slvr.TimetableSolverInputs(
            school_id=lesson.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Check outcome - note the checks get performed at instantiation
        assert len(data.error_messages) == 1
        error = data.error_messages[0]
        assert "solver defined time slot(s) was passed as solver input data!" in error
