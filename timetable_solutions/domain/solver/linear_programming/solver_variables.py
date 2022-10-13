"""Module defining the handling of PuLP variables by the solver"""

# Standard library imports
from collections import namedtuple
from typing import Dict

# Third party imports
import pulp as lp

# Local application imports
from domain.solver.solver_input_data import TimetableSolverInputs


# Keys for the different dictionaries used to store variables
var_key = namedtuple("var_key", "class_id slot_id")  # Decision variables
doubles_var_key = namedtuple("doubles_var_key", "class_id slot_1_id slot_2_id")  # Double period variables


class TimetableSolverVariables:
    """
    Class to stored solver inputs needed to define the variables, and implement the methods needed to instantiate and
    process them.
    """

    def __init__(self,
                 inputs: TimetableSolverInputs,
                 set_variables: bool = True):
        """
        :param inputs: data used to create the data - one decision variable is created per unique (class, slot)
        :param set_variables: - whether or not to instantiate all variables at the point of class instantiation
        """
        self._inputs = inputs

        if set_variables:
            self.decision_variables = self._get_decision_variables()
            self.double_period_variables = self._get_double_period_variables()

            if not self._inputs.solution_specification.allow_split_classes_within_each_day:
                # For now, we only need these variables in this instance
                self.single_period_variables = self._get_single_period_variables()

    def _get_decision_variables(self, strip: bool = True) -> Dict[var_key, lp.LpVariable]:
        """
        Method to get the pulp decision variables used to solve the timetabling problem.
        For each (unsolved class, timetable slot) pair, there is a binary variable indicating whether that class happens
        at that time
        :return - Dictionary of pulp variables, indexed by unique class / timetable slot tuples
        """
        variables = {
            var_key(class_id=unsolved_class.class_id, slot_id=timetable_slot.slot_id): lp.LpVariable(
                f"{unsolved_class.class_id}_occurs_at_slot_{timetable_slot.slot_id}", cat="Binary") for
            unsolved_class in self._inputs.unsolved_classes for timetable_slot in self._inputs.timetable_slots
        }
        if strip:
            self._strip_decision_variables(variables=variables)
        return variables

    def _strip_decision_variables(self, variables: Dict[var_key, lp.LpVariable]) -> None:
        """
        Method to remove variables corresponding to classes that are already known to occur at a certain time, since we
        know their value must be 1, so do not want to slow down the solver unnecessarily.
        Known class times are then handled when defining the constraints.
        """
        for fixed_class in self._inputs.fixed_classes:
            for timetable_slot in fixed_class.time_slots.all():
                variable_key = var_key(class_id=fixed_class.class_id, slot_id=timetable_slot.slot_id)
                if variable_key in variables.keys():
                    # No need to access the timetable_slot's slot_id, since this is how it's stored on the FixedClass
                    variables.pop(variable_key)

    # DEPENDENT VARIABLES
    def _get_double_period_variables(self) -> Dict[doubles_var_key, lp.LpVariable]:
        """
        Method to get the pulp dependent variables used to decide when double-periods should go.
        For each (unsolved class, double period) pair, there is a binary variable indicating whether that class has
        a double period at that time
        :return - Dictionary of pulp variables, indexed by class / consecutive period tuples
        """
        variables = {}  # Dict comp a bit too long here
        for unsolved_class in self._inputs.unsolved_classes:
            if unsolved_class.n_double_periods == 0:
                continue
            for double_p in self._inputs.consecutive_slots:
                var_key = doubles_var_key(class_id=unsolved_class.class_id,
                                          slot_1_id=double_p[0].slot_id, slot_2_id=double_p[1].slot_id)
                var_name = f"{unsolved_class.class_id}_double_period_at_{double_p[0].slot_id}_{double_p[1].slot_id}"
                variable = lp.LpVariable(var_name, cat="Binary")
                variables[var_key] = variable
        return variables

    def _get_single_period_variables(self) -> Dict[var_key, lp.LpVariable]:
        """
        Method to get the pulp dependent variables used to decide when single periods should go.
        Note that by 'single period' we mean that UnsolvedClass A has a single period at slot 2 if and only if class A
        occurs at slot 2, and does not occur at slot 1 and slot 3.
        :return - Dictionary of pulp variables, indexed by unique class / timetable slot tuples.

        Notes: decision variables must already be set, as there is a one-to-one correspondence with them.
        """
        variables = {key: lp.LpVariable(f"{key.class_id}_single_period_at_{key.slot_id}", cat="Binary") for
                     key in self.decision_variables.keys()}
        return variables
