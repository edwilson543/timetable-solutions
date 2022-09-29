"""
Module defining the constraints on the timetabling problem
"""
# Standard library imports
from typing import Generator, TypeVar

# Third party imports
import pulp as lp

# Local application imports
from .solver_input_data import TimetableSolverInputs
from .solver_variables import TimetableSolverVariables


LpProblem = TypeVar("LpProblem", bound=lp.LpProblem)  # Type hint to use for referencing lp problem subclasses


class TimetableSolverConstraints:

    def __init__(self,
                 inputs: TimetableSolverInputs,
                 variables: TimetableSolverVariables):
        self._inputs = inputs
        self._variables = variables

    def add_constraints_to_problem(self, problem: LpProblem) -> None:
        """
        Method add all constraints to the passed problem
        :param problem - an instance of TimetableSolver, which is a subclass of pulp.LpProblem
        """

    def _get_all_pupil_constraints(self) -> Generator[lp.LpConstraint]:
        """
        Method defining the constraints that each pupil can only be in one class at a time,and returning these as a
        generator that is iterated through once to add each one to the LpProblem
        """
        def pupil_constraint(pupil: int) -> lp.LpConstraint:
            """
            Defines the one-class-at-a-time constraint for and individual pupil, across every timeslot.
            :param pupil - represented by their id number, an integer
            """
            for timeslot in self._inputs.timetable_slot_data:
                pass
            constraint = lp.lpSum([self._variables])
            return constraint
        return (pupil_constraint(pupil) for pupil in self.inputs.pupil_list)
        pass

    def _get_all_teacher_constraints(self) -> Generator[lp.LpConstraint]:
        pass

    def _get_all_fulfillment_constraints(self) -> Generator[lp.LpConstraint]:
        pass
