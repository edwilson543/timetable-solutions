"""
Tests for specific solver solutions where one of the optional, structural
constraints determines the solution.
"""

# Third party imports
import pulp as lp
import pytest

# Local application imports
from data.constants import Day
from tests import data_factories, domain_factories
from tests.integration.domain.solver.linear_programming import helpers


@pytest.mark.django_db
class TestNosplitLessonsConstraint:
    """
    Tests for the constraint stating that a lesson may not occur at different
    times withing a single day.
    """

    def test_lesson_solution_forced_to_different_day_when_no_split_lessons(self):
        """
        Test scenario targeted at the no split lessons in a day constraint
        We have the following setup:
        Timetable structure:
            Monday: Fixed-empty-empty;
            Tuesday: empty;
            Tuesday: 1 slot
        1 Lesson, requiring:
            2 total slots;
            0 double periods.
        By the no split lessons constraint, the remaining class has to be taught on Tuesday. In particular, it cannot be
        taught at period 3 on Monday. (And not at period 2 on Monday since we want 0 doubles.
        """
        pupil = data_factories.Pupil()
        yg = pupil.year_group
        mon_1 = data_factories.TimetableSlot(
            day_of_week=Day.MONDAY,
            school=pupil.school,
            relevant_year_groups=(yg,),
        )
        mon_2 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_1)
        mon_3 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_2)
        tue_1 = data_factories.TimetableSlot(
            day_of_week=Day.TUESDAY, school=pupil.school, relevant_year_groups=(yg,)
        )
        lesson = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=2,
            total_required_double_periods=0,
            user_defined_time_slots=(mon_1,),
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        spec = domain_factories.SolutionSpecification(
            allow_split_lessons_within_each_day=False
        )
        solver_ = helpers.get_solution(school=lesson.school, spec=spec)

        # Check solution is a solved slot on tuesday
        assert solver_.problem.status == lp.LpStatusOptimal

        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, tue_1)
        assert not helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_2)
        assert not helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_3)

    def test_triple_period_not_allowed_when_no_triples(self):
        """
        Test scenario targeted at the no two doubles in a day constraint (which is effectively also a no triples+
        constraint)
        We have the following setup:
        Timetable structure:
            Monday: empty-empty-empty-Fixed;
            Tuesday: empty-empty;
        1 Lesson, requiring:
            4 total slots;
            2 double period.
        By the no two doubles in a day constraint, we must have the following final structure:
            Monday: A - Solver-Solver-empty-User; OR B - Solver-empty-Solver-User - but we make the pupil /
            classroom / teacher incompatible with option B, so we always get option A
            Tuesday: Solver-Solver
        """
        pupil = data_factories.Pupil()
        yg = pupil.year_group
        mon_1 = data_factories.TimetableSlot(
            day_of_week=Day.MONDAY,
            school=pupil.school,
            relevant_year_groups=(yg,),
        )
        mon_2 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_1)
        mon_3 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_2)
        mon_4 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_3)
        tue_1 = data_factories.TimetableSlot(
            day_of_week=Day.TUESDAY, school=pupil.school, relevant_year_groups=(yg,)
        )
        tue_2 = data_factories.TimetableSlot.get_next_consecutive_slot(tue_1)
        lesson = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=4,
            total_required_double_periods=2,
            user_defined_time_slots=(mon_4,),
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        spec = domain_factories.SolutionSpecification(
            allow_triple_periods_and_above=False
        )
        solver_ = helpers.get_solution(school=lesson.school, spec=spec)

        # Check solution is as expected
        assert solver_.problem.status == lp.LpStatusOptimal

        assert not helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_1)
        assert not helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_2)
        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_3)
        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, tue_1)
        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, tue_2)

    def test_no_split_lessons_no_triples_combined(self):
        """
        Test scenario targeted at using the no two doubles in a day constraint in combination with the no split lessons
        constraint, as well as testing that the no split lessons constraint isn't broken by a user-defined split
        We have the following setup:
        Timetable structure:
            Monday: empty-empty-empty;
            Tuesday: empty-empty-empty;
            Wednesday: empty
        1 Lesson, requiring:
            5 total slots;
            2 double period.
        Therefore, we expect a double at some point on Monday, a double at some point on Tuesday, and a single on
        Wednesday.
        """
        pupil = data_factories.Pupil()
        yg = pupil.year_group
        mon_1 = data_factories.TimetableSlot(
            day_of_week=Day.MONDAY,
            school=pupil.school,
            relevant_year_groups=(yg,),
        )
        mon_2 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_1)
        mon_3 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_2)
        tue_1 = data_factories.TimetableSlot(
            day_of_week=Day.TUESDAY, school=pupil.school, relevant_year_groups=(yg,)
        )
        tue_2 = data_factories.TimetableSlot.get_next_consecutive_slot(tue_1)
        tue_3 = data_factories.TimetableSlot.get_next_consecutive_slot(tue_2)
        wed_1 = data_factories.TimetableSlot(
            day_of_week=Day.WEDNESDAY, school=pupil.school, relevant_year_groups=(yg,)
        )

        lesson = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=5,
            total_required_double_periods=2,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        spec = domain_factories.SolutionSpecification(
            allow_triple_periods_and_above=False,
            allow_split_lessons_within_each_day=False,
        )
        solver_ = helpers.get_solution(school=lesson.school, spec=spec)

        # Check solution is as expected
        assert solver_.problem.status == lp.LpStatusOptimal

        # Check we have on double on monday
        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_2)
        assert helpers.lesson_occurs_at_slot(
            solver_.variables, lesson, mon_1
        ) or helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_3)
        assert (
            not helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_1)
        ) or (not helpers.lesson_occurs_at_slot(solver_.variables, lesson, mon_3))

        # Check we have on double on tuesday
        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, tue_2)
        assert helpers.lesson_occurs_at_slot(
            solver_.variables, lesson, tue_1
        ) or helpers.lesson_occurs_at_slot(solver_.variables, lesson, tue_3)
        assert (
            not helpers.lesson_occurs_at_slot(solver_.variables, lesson, tue_1)
        ) or (not helpers.lesson_occurs_at_slot(solver_.variables, lesson, tue_3))

        # Check single on wednesday
        assert helpers.lesson_occurs_at_slot(solver_.variables, lesson, wed_1)
