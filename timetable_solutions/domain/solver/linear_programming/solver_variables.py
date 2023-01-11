"""
Module defining the storage and handling of PuLP variables by the solver.
"""

# Standard library imports
from collections import namedtuple

# Third party imports
import pulp as lp

# Local application imports
from domain.solver.solver_input_data import TimetableSolverInputs


# Keys for the different dictionaries used to store variables
var_key = namedtuple("var_key", "lesson_id slot_id")  # Decision variables
doubles_var_key = namedtuple(  # Double period variables
    "doubles_var_key", "lesson_id slot_1_id slot_2_id"
)


class TimetableSolverVariables:
    """
    Class to define the PuLP variables, and implement the methods needed to instantiate and process them.
    """

    def __init__(self, inputs: TimetableSolverInputs):
        """
        :param inputs: data used to create the data - one decision variable is created per unique (class, slot)
        """
        self._inputs = inputs

        self.decision_variables = self._get_decision_variables()
        self.double_period_variables = self._get_double_period_variables()

    def _get_decision_variables(
        self, strip: bool = True
    ) -> dict[var_key, lp.LpVariable]:
        """
        Method to get the pulp decision variables used to solve the timetabling problem.
        For each (lesson, timetable slot) pair, there is a binary variable indicating whether that class happens
        at that time.
        :return - Dictionary of pulp variables, indexed by unique class / timetable slot tuples
        """
        variables = {
            var_key(
                lesson_id=lesson.lesson_id, slot_id=timetable_slot.slot_id
            ): lp.LpVariable(
                f"{lesson.lesson_id}_occurs_at_slot_{timetable_slot.slot_id}",
                cat="Binary",
            )
            for lesson in self._inputs.lessons
            for timetable_slot in lesson.get_associated_timeslots()
        }
        if strip:
            self._strip_decision_variables(variables=variables)
        return variables

    def _strip_decision_variables(
        self, variables: dict[var_key, lp.LpVariable]
    ) -> None:
        """
        Method to remove variables corresponding to times when we already know lessons occur.
        (i.e. we know their value must be 1, so do not want to slow down the solver unnecessarily.)
        Known class times are then handled when defining the constraints.
        """
        for lesson in self._inputs.lessons:
            for timetable_slot in lesson.user_defined_time_slots.all():
                variable_key = var_key(
                    lesson_id=lesson.lesson_id, slot_id=timetable_slot.slot_id
                )
                variables.pop(variable_key)

    # DEPENDENT VARIABLES
    def _get_double_period_variables(self) -> dict[doubles_var_key, lp.LpVariable]:
        """
        Method to get the pulp dependent variables used to decide when double-periods should go.
        For each (lesson, double period) pair, there is a binary variable indicating whether that class has
        a double period at that time
        :return - Dictionary of pulp variables, indexed by class / consecutive period tuples
        """
        variables = {}  # Dict comp a bit too long here
        for lesson in self._inputs.lessons:

            if lesson.total_required_double_periods == 0:
                continue

            relevant_year_group = lesson.get_relevant_year_group().year_group
            for (
                consecutive_slot_pair
            ) in self._inputs.get_consecutive_slots_for_year_group(
                year_group=relevant_year_group
            ):

                key = doubles_var_key(
                    lesson_id=lesson.lesson_id,
                    slot_1_id=consecutive_slot_pair[0].slot_id,
                    slot_2_id=consecutive_slot_pair[1].slot_id,
                )
                var_name = (
                    f"{lesson.lesson_id}_double_period_at_{consecutive_slot_pair[0].slot_id}_"
                    f"{consecutive_slot_pair[1].slot_id}"
                )
                variable = lp.LpVariable(var_name, cat="Binary")
                variables[key] = variable

        return variables
