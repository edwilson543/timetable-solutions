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
