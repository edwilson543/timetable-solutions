# Third party imports
import pytest

# Local application imports
from domain import solver
from tests import data_factories, domain_factories


@pytest.mark.django_db
class TestSolverSolutionPupilConstraintDriven:
    """Tests for solver solutions where the availability of a pupil drives the solution."""

    def test_pupil_is_only_allocated_one_lesson_at_a_time(self):
        """
        There is one pupil, who must go to 2 classes.
        There are 2 time slots. There are no user defined time slots, or other constraints.
        """
        pupil = data_factories.Pupil()
        data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        # Male two lessons put the pupil in both of them
        lesson_a = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )
        lesson_b = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=pupil.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Assert the lessons only have one slot, and occur at different times
        assert lesson_a.solver_defined_time_slots.count() == 1
        assert lesson_b.solver_defined_time_slots.count() == 1
        assert (
            lesson_a.solver_defined_time_slots.get()
            != lesson_b.solver_defined_time_slots.get()
        )

    def test_pupil_is_only_allocated_one_lesson_at_a_time_when_has_fixed_slot(self):
        """
        There is one pupil, who must go to 2 classes.
        There are 2 time slots, and one of the lessons is fixed at one of these.
        """
        pupil = data_factories.Pupil()
        slot_1 = data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        slot_2 = data_factories.TimetableSlot(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
        )
        # Male two lessons our pupil must be able to attend
        lesson_a = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
            user_defined_time_slots=(slot_1,),
        )
        lesson_b = data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )

        # Solve the timetabling problem
        solver.produce_timetable_solutions(
            school_access_key=pupil.school.school_access_key,
            solution_specification=domain_factories.SolutionSpecification(),
        )

        # Assert the lessons only have one slot, and occur at different times
        assert lesson_a.solver_defined_time_slots.count() == 0
        assert lesson_b.solver_defined_time_slots.get() == slot_2
