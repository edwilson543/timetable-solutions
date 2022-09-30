"""
Module defining the constraints on the timetabling problem
"""
# Standard library imports
from typing import Generator, TypeVar, Dict, Tuple

# Third party imports
import pulp as lp

# Local application imports
from data import models
from .solver_input_data import TimetableSolverInputs
from .solver_variables import var_key


LpProblem = TypeVar("LpProblem", bound=lp.LpProblem)  # Type hint to use for referencing l_p problem subclasses


class TimetableSolverConstraints:

    def __init__(self,
                 inputs: TimetableSolverInputs,
                 variables: Dict[var_key, lp.LpVariable]):
        self._inputs = inputs
        self._variables = variables

    def add_constraints_to_problem(self, problem: LpProblem) -> None:
        """
        Method add all constraints to the passed problem
        :param problem - an instance of TimetableSolver, which is a subclass of pulp.LpProblem
        """
        pass

    def _get_all_pupil_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each pupil can only be in one class at a time,and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem
        """

        def one_place_at_a_time_constraint(
                pupil: models.Pupil, time_slot: models.TimetableSlot) -> Tuple[lp.LpConstraint, str] | None:
            """
            Defines the one-class-at-a-time constraint for and individual pupil, and individual timeslot.
            :param pupil - represented by their id number, an integer
            :param time_slot - represented by the slot_id number, an integer

            We sum the variables at a fixed time slot over the unsolved classes, but then force this to 0 if the pupil
            already has an existing commitment
            """
            existing_commitment = pupil.check_if_busy_at_time_slot(slot=time_slot)
            possible_commitments = lp.lpSum(
                [self._variables[key] for usc in self._inputs.unsolved_classes if (pupil in usc.pupils.all()) and
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

    def _get_all_teacher_constraints(self) -> Generator[lp.LpConstraint, None, None]:
        pass

    def _get_all_fulfillment_constraints(self) -> Generator[lp.LpConstraint, None, None]:
        pass
