"""
Module defining the constraints on the timetabling problem
"""
# Standard library imports
from typing import Generator, Dict, Tuple

# Third party imports
import pulp as lp

# Local application imports
from data import models
from .solver_input_data import TimetableSolverInputs
from .solver_variables import var_key


# TODO add min distinct slots constraint - or alternative improvement

class TimetableSolverConstraints:

    def __init__(self,
                 inputs: TimetableSolverInputs,
                 variables: Dict[var_key, lp.LpVariable]):
        self._inputs = inputs
        self._variables = variables

    def add_constraints_to_problem(self, problem: lp.LpProblem) -> None:
        """
        Method to add all constraints to the passed problem - what this class is used for outside this module.
        :param problem - an instance of pulp.LpProblem, which collects constraints/objective and solves
        :return None - since the passed problem will be modified in-place
        """
        fulfillment_constraints = self._get_all_fulfillment_constraints()
        for constraint in fulfillment_constraints:
            problem += constraint

        pupil_constraints = self._get_all_pupil_constraints()
        for constraint in pupil_constraints:
            problem += constraint

        teacher_constraints = self._get_all_teacher_constraints()
        for constraint in teacher_constraints:
            problem += constraint

        classroom_constraints = self._get_all_classroom_constraints()
        for constraint in classroom_constraints:
            problem += constraint

    def _get_all_fulfillment_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each unsolved class must be taught for the required number of periods.
        """
        def fulfillment_constraint(unsolved_class: models.UnsolvedClass) -> Tuple[lp.LpConstraint, str]:
            """
            States that the passed unsolved_class must be taught for the number of required periods, less any
            existing FixedClass timeslots
            """
            variables_sum = lp.lpSum(
                [var for var_key, var in self._variables.items() if var_key.class_id == unsolved_class.class_id])

            corresponding_fixed_class = self._inputs.fixed_classes.filter(class_id=unsolved_class.class_id)
            if corresponding_fixed_class.count() == 1:
                corresponding_fixed_class = corresponding_fixed_class.first()
                existing_commitments = corresponding_fixed_class.time_slots.all().count()
            else:
                existing_commitments = 0

            constraint = (variables_sum <= (unsolved_class.total_slots - existing_commitments),
                          f"usc_{unsolved_class.class_id}_taught_for_{unsolved_class.total_slots}")
            return constraint

        constraints = (fulfillment_constraint(unsolved_class) for unsolved_class in self._inputs.unsolved_classes)
        return constraints

    def _get_all_pupil_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each pupil can only be in one class at a time,and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem
        """

        def one_place_at_a_time_constraint(
                pupil: models.Pupil, time_slot: models.TimetableSlot) -> Tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-place-at-a-time' constraint for an individual pupil, and individual timeslot.
            We sum the unsolved class variables relevant to the pupil, and force this to 0 if the pupil has an
            existing commitment at the fixed time slot. Otherwise their sum must be max 1.
            """
            existing_commitment = pupil.check_if_busy_at_time_slot(slot=time_slot)
            possible_commitments = lp.lpSum(
                [self._variables.get(key) for usc in self._inputs.unsolved_classes if (pupil in usc.pupils.all()) and
                 (key := var_key(class_id=usc.class_id, slot_id=time_slot.slot_id)) in self._variables.keys()]
            )
            if existing_commitment:
                constraint = (possible_commitments == 0,
                              f"pupil_{pupil.pupil_id}_unavailable_at_{time_slot.slot_id}")
            else:
                constraint = (possible_commitments <= 1,
                              f"pupil_{pupil.pupil_id}_available_at_{time_slot.slot_id}")
            return constraint

        constraints = (one_place_at_a_time_constraint(pupil=pupil, time_slot=time_slot) for
                       pupil in self._inputs.pupils for time_slot in self._inputs.timetable_slots)
        return constraints

    def _get_all_teacher_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each teacher can only teach one class at a time, and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem
        """

        def one_place_at_a_time_constraint(
                teacher: models.Teacher, time_slot: models.TimetableSlot) -> Tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-place-at-a-time' constraint for an individual teacher, and individual timeslot.
            We sum the unsolved class variables relevant to the teacher, and force this to 0 if the teacher has an
            existing commitment at the fixed time slot. Otherwise their sum must be max 1.
            """
            existing_commitment = teacher.check_if_busy_at_time_slot(slot=time_slot)
            possible_commitments = lp.lpSum(
                [self._variables.get(key) for usc in self._inputs.unsolved_classes if (teacher == usc.teacher) and
                 (key := var_key(class_id=usc.class_id, slot_id=time_slot.slot_id)) in self._variables.keys()]
            )
            if existing_commitment:
                constraint = (possible_commitments == 0,
                              f"teacher_{teacher.teacher_id}_unavailable_at_{time_slot.slot_id}")
            else:
                constraint = (possible_commitments <= 1,
                              f"teacher_{teacher.teacher_id}_available_at_{time_slot.slot_id}")
            return constraint

        constraints = (one_place_at_a_time_constraint(teacher=teacher, time_slot=time_slot) for
                       teacher in self._inputs.teachers for time_slot in self._inputs.timetable_slots)
        return constraints

    def _get_all_classroom_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each classroom can only host one class at a time, and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem.
        """

        def one_class_at_a_time_constraint(
                classroom: models.Classroom, time_slot: models.TimetableSlot) -> Tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-class-at-a-time' constraint for an individual classroom, and individual timeslot.
            We sum the unsolved class variables relevant to the classroom, and force this to 0 if the teacher has an
            existing commitment at the fixed time slot. Otherwise their sum must be max 1.
            """
            occupied = classroom.check_if_occupied_at_time_slot(slot=time_slot)
            possible_uses = lp.lpSum(
                [self._variables.get(key) for usc in self._inputs.unsolved_classes if (classroom == usc.classroom) and
                 (key := var_key(class_id=usc.class_id, slot_id=time_slot.slot_id)) in self._variables.keys()]
            )
            if occupied:
                constraint = (possible_uses == 0,
                              f"classroom_{classroom.classroom_id}_occupied_at_{time_slot.slot_id}")
            else:
                constraint = (possible_uses <= 1,
                              f"classroom_{classroom.classroom_id}_unoccupied_at_{time_slot.slot_id}")
            return constraint

        constraints = (one_class_at_a_time_constraint(classroom=classroom, time_slot=time_slot) for
                       classroom in self._inputs.classrooms for time_slot in self._inputs.timetable_slots)
        return constraints
