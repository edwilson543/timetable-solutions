# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp
import pytest

# Local application imports
from data import constants as data_constants
from domain import solver as slvr
from tests import data_factories
from tests import domain_factories


@pytest.mark.django_db
class TestSolverSolutionClassroomConstraintDriven:
    """Tests for solver solutions where the availability of a classroom drives the solution."""

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
        slot_1 = data_factories.TimetableSlot(
            relevant_year_groups=(yg_1,),
            school=classroom.school,
            day_of_week=data_constants.Day.MONDAY,
        )

        # Make a lesson with 2 slot choices, once clashing with slot_1
        lesson_2 = data_factories.Lesson.with_n_pupils(
            classroom=classroom,
            school=classroom.school,
            total_required_slots=1,
            total_required_double_periods=0,
        )
        yg_2 = lesson_2.pupils.first().year_group
        slot_1_clash = data_factories.TimetableSlot(
            relevant_year_groups=(yg_2,),
            school=classroom.school,
            starts_at=dt.time(
                hour=slot_1.starts_at.hour, minute=clash_slot_overlap_minutes
            ),
            ends_at=dt.time(
                hour=slot_1.ends_at.hour, minute=clash_slot_overlap_minutes
            ),
            day_of_week=data_constants.Day.MONDAY,
        )
        lesson_2_forced_slot = data_factories.TimetableSlot(
            relevant_year_groups=(yg_2,),
            school=classroom.school,
            starts_at=slot_1.starts_at,
            ends_at=slot_1.ends_at,
            day_of_week=data_constants.Day.TUESDAY,  # Note different day
        )

        # Solve the problem for this school
        spec = domain_factories.SolutionSpecification()
        data = slvr.TimetableSolverInputs(
            school_id=classroom.school.school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)
        solver.solve()

        # Check solved & solution as expected
        assert lp.LpStatus[solver.problem.status] == "Optimal"

        dec_vars = solver.variables.decision_variables

        # Check lesson 1 is at its only option slot
        forced_var = slvr.var_key(slot_id=slot_1.slot_id, lesson_id=lesson_1.lesson_id)
        assert dec_vars[forced_var] == 1

        # Check lesson 2 not at the clashed slot
        clash_var = slvr.var_key(
            slot_id=slot_1_clash.slot_id, lesson_id=lesson_2.lesson_id
        )
        assert dec_vars[clash_var] == 0

        # Check lesson 2 therefore at the other slot
        sol_var_2 = slvr.var_key(
            slot_id=lesson_2_forced_slot.slot_id, lesson_id=lesson_2.lesson_id
        )
        assert dec_vars[sol_var_2] == 0
