# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data.constants import Day
from domain import solver
from tests import data_factories, domain_factories


@pytest.mark.django_db
class TestSolverSolutionClassroomConstraintDriven:
    """Tests for solver solutions where the availability of a classroom drives the solution."""

    def test_classroom_is_only_allocated_one_lesson_at_a_time(self):
        """
        A classroom must host 2 lessons.
        Both use 1 slot, and there are 2 possible time slots.
        """
        classroom = data_factories.Classroom()
        pupil = data_factories.Pupil(school=classroom.school)
        data_factories.TimetableSlot(
            school=classroom.school,
            relevant_year_groups=(pupil.year_group,),
        )
        data_factories.TimetableSlot(
            school=classroom.school,
            relevant_year_groups=(pupil.year_group,),
        )
        # Male two lessons and allocate both to the same teacher
        lesson_a = data_factories.Lesson(
            school=classroom.school,
            total_required_slots=1,
            total_required_double_periods=0,
            classroom=classroom,
            pupils=(pupil,),
        )
        lesson_b = data_factories.Lesson(
            school=classroom.school,
            total_required_slots=1,
            total_required_double_periods=0,
            classroom=classroom,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=classroom.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Assert the lessons only have one slot, and occur at different times
        assert lesson_a.solver_defined_time_slots.count() == 1
        assert lesson_b.solver_defined_time_slots.count() == 1
        assert (
            lesson_a.solver_defined_time_slots.get()
            != lesson_b.solver_defined_time_slots.get()
        )

    def test_classroom_is_only_allocated_one_lesson_at_a_time_when_has_fixed_slot(self):
        """
        A classroom must host 2 lessons.
        Both use 1 slot, there are 2 possible time slots,
        one lesson is fixed at one of the slots.
        """
        classroom = data_factories.Classroom()
        pupil = data_factories.Pupil(school=classroom.school)
        slot_1 = data_factories.TimetableSlot(
            school=classroom.school,
            relevant_year_groups=(pupil.year_group,),
        )
        slot_2 = data_factories.TimetableSlot(
            school=classroom.school,
            relevant_year_groups=(pupil.year_group,),
        )
        # Male two lessons and allocate both to the same teacher
        lesson_a = data_factories.Lesson(
            school=classroom.school,
            total_required_slots=1,
            total_required_double_periods=0,
            classroom=classroom,
            pupils=(pupil,),
            user_defined_time_slots=(slot_1,),
        )
        lesson_b = data_factories.Lesson(
            school=classroom.school,
            total_required_slots=1,
            total_required_double_periods=0,
            classroom=classroom,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=classroom.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Assert the lessons only have one slot, and occur at different times
        assert lesson_a.solver_defined_time_slots.count() == 0
        assert lesson_b.solver_defined_time_slots.get() == slot_2

    @pytest.mark.parametrize("clash_slot_overlap_minutes", [0, 30])
    def test_classroom_has_two_year_groups_at_clashing_times(
        self, clash_slot_overlap_minutes: int
    ):
        """
        One classroom hosts two lessons each requiring one slot.
        The first lesson only has one slot choice for when it can go.
        The second slot has two choices of slot, but one clashes with the first lesson's only choice.
        Since the classroom can only have one lesson at a time, the second lesson is determined.
        """
        classroom = data_factories.Classroom()

        # Make a lesson with only 1 slot choice
        lesson_1 = data_factories.Lesson.with_n_pupils(
            classroom=classroom,
            school=classroom.school,
            total_required_slots=1,
            total_required_double_periods=0,
        )
        yg_1 = lesson_1.pupils.first().year_group
        lesson_1_forced_slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg_1,),
            school=classroom.school,
            day_of_week=Day.MONDAY,
        )

        # Make a lesson with 2 slot choices, once clashing with slot_1
        lesson_2 = data_factories.Lesson.with_n_pupils(
            classroom=classroom,
            school=classroom.school,
            total_required_slots=1,
            total_required_double_periods=0,
        )
        yg_2 = lesson_2.pupils.first().year_group
        data_factories.TimetableSlot(
            relevant_year_groups=(yg_2,),
            school=classroom.school,
            starts_at=dt.time(
                hour=lesson_1_forced_slot.starts_at.hour,
                minute=clash_slot_overlap_minutes,
            ),
            ends_at=dt.time(
                hour=lesson_1_forced_slot.ends_at.hour,
                minute=clash_slot_overlap_minutes,
            ),
            day_of_week=Day.MONDAY,
        )
        lesson_2_forced_slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg_2,),
            school=classroom.school,
            starts_at=lesson_1_forced_slot.starts_at,
            ends_at=lesson_1_forced_slot.ends_at,
            day_of_week=Day.TUESDAY,  # Note different day
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=classroom.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Assert the lessons only have one slot, and occur at different times
        assert lesson_1.solver_defined_time_slots.get() == lesson_1_forced_slot
        assert lesson_2.solver_defined_time_slots.get() == lesson_2_forced_slot
