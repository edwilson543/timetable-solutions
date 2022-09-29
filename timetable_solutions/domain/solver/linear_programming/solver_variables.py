"""Module defining the handling of PuLP variables by the solver"""

# Standard library imports
from collections import namedtuple
from typing import Dict, Tuple

# Third party imports
import pulp as lp

# Local application imports
from domain.solver.linear_programming.solver_input_data import TimetableSolverInputs


variables_key = namedtuple("variables_key", "class_id slot_id")  # To be used as the keys of the dictionary


class TimetableSolverVariables:
    """
    Class to stored solver inputs needed to define the variables, and implement the methods needed to instantiate and
    process them.
    """

    def __init__(self, inputs: TimetableSolverInputs):
        self._inputs = inputs

    def get_variables(self, strip: bool = True) -> Dict[Tuple, lp.LpVariable]:
        """
        Method to get the pulp variables relevant to a given solution.
        For each (unsolved class, timetable slot) pair, there is a binary variable indicating whether that class happens
        at that time
        :return - A dictionary of pulp variables, indexed by unique class / timetable slot tuples
        """
        variables = {
            variables_key(class_id=unsolved_class.class_id, slot_id=timetable_slot.slot_id): lp.LpVariable(
                f"{unsolved_class.class_id}_occurs_at_slot_{timetable_slot.slot_id}", cat="Binary") for
            unsolved_class in self._inputs.unsolved_classes for timetable_slot in self._inputs.timetable_slots
        }
        if strip:
            self._strip_variables(variables=variables)
        return variables

    def _strip_variables(self, variables: Dict[Tuple, lp.LpVariable]) -> None:
        """
        Method to remove variables corresponding to classes that are already known to occur at a certain time, since we
        know their value must be 1, so do not want to slow down the solver unnecessarily.
        Known class times are then handled when defining the constraints.

        """
        for fixed_class in self._inputs.fixed_classes:
            for timetable_slot in fixed_class.time_slots.all():
                variable_key = variables_key(class_id=fixed_class.class_id, slot_id=timetable_slot.slot_id)
                if variable_key in variables.keys():
                    # No need to access the timetable_slot's slot_id, since this is how it's stored on the FixedClass
                    variables.pop(variable_key)
