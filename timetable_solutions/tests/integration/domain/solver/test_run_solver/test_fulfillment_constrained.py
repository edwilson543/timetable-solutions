"""Tests for the solutions in scenarios driven by lesson fulfillment."""

# Third party imports
import pytest

# Local application imports
from data.constants import Day
from domain import solver
from tests import data_factories, domain_factories


@pytest.mark.django_db
class TestSolverSolutionFulfillmentConstrainDriven:
    """
    Tests for solver solutions where fulfilling the required number of slots
    per week is what drives the solution.
    """

    @pytest.mark.parametrize("total_required_slots", [1, 3])
    def test_total_required_slots_are_fulfilled(self, total_required_slots: int):
        lesson = data_factories.Lesson.with_n_pupils(
            total_required_slots=total_required_slots, total_required_double_periods=0
        )
        yg = lesson.pupils.first().year_group

        # Make one more than the total number of required slots
        for _ in range(0, total_required_slots + 1):
            data_factories.TimetableSlot(
                relevant_year_groups=(yg,), school=lesson.school
            )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=lesson.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Check the lesson now has the expected slots are set oin the lesson
        assert lesson.solver_defined_time_slots.all().count() == total_required_slots

    def test_required_slots_are_fulfilled_with_user_defined_slot(self):
        pupil = data_factories.Pupil()
        slots = [
            data_factories.TimetableSlot(
                relevant_year_groups=(pupil.year_group,), school=pupil.school
            )
            for _ in range(0, 3)
        ]
        # Make a lesson with 1 user defined slot, therefore requiring 1 solved slot
        lesson = data_factories.Lesson(
            total_required_slots=2,
            total_required_double_periods=0,
            user_defined_time_slots=(slots[0],),
            school=pupil.school,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=lesson.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Check 1 additional slot was set on the lesson
        assert lesson.solver_defined_time_slots.count() == 1


@pytest.mark.django_db
class TestSolverSolutionDoublePeriodFulfillmentConstrainDriven:
    """
    Tests for solver solutions where fulfilling the required number of double
    periods per week is what drives the solution.
    """

    def test_required_double_period_is_fulfilled(self):
        """
        Test scenario targeted at the double period fulfillment and dependency constraints.
        We have the following setup:
        Timetable structure:
            Monday: empty-empty;
            Tuesday: empty;
        1 Lesson, requiring:
            2 total slots;
            1 double period.
        Only 2 of the 3 timeslots are consecutive, so we must have the doubler period during these slots.
        """
        lesson = data_factories.Lesson.with_n_pupils(
            total_required_slots=2,
            total_required_double_periods=1,
        )
        yg = lesson.pupils.first().year_group
        mon_1 = data_factories.TimetableSlot(
            day_of_week=Day.MONDAY, school=lesson.school, relevant_year_groups=(yg,)
        )
        mon_2 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_1)
        data_factories.TimetableSlot(
            day_of_week=Day.TUESDAY, school=lesson.school, relevant_year_groups=(yg,)
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=lesson.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Check the lesson now has the solution set
        assert set(lesson.solver_defined_time_slots.all()) == {mon_1, mon_2}

    def test_double_period_only_fulfilled_if_teams_up_with_user_defined_slots(self):
        """
        Test scenario targeted at the double period fulfillment and dependency constraints, in the particular instance
        where a user defined slot comes into play.

        We have the following setup:
        Timetable structure:
            Monday: empty-empty;
            Tuesday: empty-fixed;
        1 Lesson, requiring:
            2 total slots;
            1 double period.
        Therefore, the solution is to attach a second slot to the already defined slot, making the double.
        """
        pupil = data_factories.Pupil()
        yg = pupil.year_group
        mon_1 = data_factories.TimetableSlot(
            day_of_week=Day.MONDAY, school=pupil.school, relevant_year_groups=(yg,)
        )
        data_factories.TimetableSlot.get_next_consecutive_slot(mon_1)
        tue_1 = data_factories.TimetableSlot(
            day_of_week=Day.TUESDAY, school=pupil.school, relevant_year_groups=(yg,)
        )
        tue_2 = data_factories.TimetableSlot.get_next_consecutive_slot(tue_1)
        lesson = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=2,
            total_required_double_periods=1,
            user_defined_time_slots=(tue_2,),
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=lesson.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Check the lesson now has the solution set
        assert lesson.solver_defined_time_slots.get() == tue_1

    def test_only_one_double_forces_slot_on_different_day(self):
        """
        Test scenario targeted at the component of the double period dependency constraint which states that adding an
        solver defined lesson next to a user defined lesson results in a double period.
        We have the following setup:
        Timetable structure:
            Monday: Fixed-Fixed-empty-empty-Fixed;
            Tuesday: empty;
        1 Lesson, requiring:
            4 total slots;
            1 double period.
        Since there is already a double on Monday, and adding a single in either of the available slots would create
        another double, the class must go on the Tuesday.
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
        mon_5 = data_factories.TimetableSlot.get_next_consecutive_slot(mon_4)
        tue_1 = data_factories.TimetableSlot(
            day_of_week=Day.TUESDAY, school=pupil.school, relevant_year_groups=(yg,)
        )
        lesson = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=4,
            total_required_double_periods=1,
            user_defined_time_slots=(mon_1, mon_2, mon_5),
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=lesson.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Check the lesson now has the solution set
        assert lesson.solver_defined_time_slots.get() == tue_1
