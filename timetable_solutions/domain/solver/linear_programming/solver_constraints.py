"""
Module defining the constraints on the timetabling problem
"""
# Standard library imports
import itertools
from typing import Generator, Tuple

# Third party imports
import pulp as lp

# Local application imports
from data import models
from domain.solver.solver_input_data import TimetableSolverInputs
from domain.solver.linear_programming.solver_variables import TimetableSolverVariables
from .solver_variables import var_key, doubles_var_key


class TimetableSolverConstraints:
    """
    Class used to define the constraints for the given timetabling problem, and then add them a LpProblem instance
    """

    def __init__(self,
                 inputs: TimetableSolverInputs,
                 variables: TimetableSolverVariables):
        self._inputs = inputs
        self._decision_variables = variables.decision_variables
        self._double_period_variables = variables.double_period_variables

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

        double_period_fulfillment_constraints = self._get_all_double_period_fulfillment_constraints()
        for constraint in double_period_fulfillment_constraints:
            problem += constraint

        double_period_dependency_constraints = self._get_all_double_period_dependency_constraints()
        for constraint in double_period_dependency_constraints:
            problem += constraint

        if not self._inputs.solution_specification.allow_split_classes_within_each_day:
            double_period_no_repetition_constraints = self._get_all_no_two_double_periods_in_a_day_constraints()
            for constraint in double_period_no_repetition_constraints:
                problem += constraint

    def _get_all_fulfillment_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each unsolved class must be taught for the required number of periods.
        """
        def __fulfillment_constraint(unsolved_class: models.UnsolvedClass) -> Tuple[lp.LpConstraint, str]:
            """
            States that the passed unsolved_class must be taught for the number of required periods, less any
            existing FixedClass timeslots
            """
            variables_sum = lp.lpSum([var for key, var in self._decision_variables.items()
                                      if key.class_id == unsolved_class.class_id])

            corresponding_fixed_class = self._inputs.fixed_classes.filter(class_id=unsolved_class.class_id)
            if corresponding_fixed_class.count() == 1:
                corresponding_fixed_class = corresponding_fixed_class.first()
                existing_commitments = corresponding_fixed_class.time_slots.all().count()
            else:
                existing_commitments = 0

            constraint = (variables_sum == (unsolved_class.total_slots - existing_commitments),
                          f"usc_{unsolved_class.class_id}_taught_for_{unsolved_class.total_slots}")
            return constraint

        constraints = (__fulfillment_constraint(unsolved_class) for unsolved_class in self._inputs.unsolved_classes)
        return constraints

    def _get_all_pupil_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each pupil can only be in one class at a time,and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem
        """

        def __one_place_at_a_time_constraint(
                pupil: models.Pupil, time_slot: models.TimetableSlot) -> Tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-place-at-a-time' constraint for an individual pupil, and individual timeslot.
            We sum the unsolved class variables relevant to the pupil, and force this to 0 if the pupil has an
            existing commitment at the fixed time slot. Otherwise their sum must be max 1.
            """
            existing_commitment = pupil.check_if_busy_at_time_slot(slot=time_slot)
            possible_commitments = lp.lpSum(
                [self._decision_variables.get(key) for usc in self._inputs.unsolved_classes
                 if (pupil in usc.pupils.all()) and
                 (key := var_key(class_id=usc.class_id, slot_id=time_slot.slot_id)) in self._decision_variables.keys()]
            )
            if existing_commitment:
                constraint = (possible_commitments == 0,
                              f"pupil_{pupil.pupil_id}_unavailable_at_{time_slot.slot_id}")
            else:
                constraint = (possible_commitments <= 1,
                              f"pupil_{pupil.pupil_id}_available_at_{time_slot.slot_id}")
            return constraint

        constraints = (__one_place_at_a_time_constraint(pupil=pupil, time_slot=time_slot) for
                       pupil in self._inputs.pupils for time_slot in self._inputs.timetable_slots)
        return constraints

    def _get_all_teacher_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each teacher can only teach one class at a time, and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem
        """

        def __one_place_at_a_time_constraint(
                teacher: models.Teacher, time_slot: models.TimetableSlot) -> Tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-place-at-a-time' constraint for an individual teacher, and individual timeslot.
            We sum the unsolved class variables relevant to the teacher, and force this to 0 if the teacher has an
            existing commitment at the fixed time slot. Otherwise their sum must be max 1.
            """
            existing_commitment = teacher.check_if_busy_at_time_slot(slot=time_slot)
            possible_commitments = lp.lpSum(
                [self._decision_variables.get(key) for usc in self._inputs.unsolved_classes
                 if (teacher == usc.teacher) and
                 (key := var_key(class_id=usc.class_id, slot_id=time_slot.slot_id)) in self._decision_variables.keys()]
            )
            if existing_commitment:
                constraint = (possible_commitments == 0,
                              f"teacher_{teacher.teacher_id}_unavailable_at_{time_slot.slot_id}")
            else:
                constraint = (possible_commitments <= 1,
                              f"teacher_{teacher.teacher_id}_available_at_{time_slot.slot_id}")
            return constraint

        constraints = (__one_place_at_a_time_constraint(teacher=teacher, time_slot=time_slot) for
                       teacher in self._inputs.teachers for time_slot in self._inputs.timetable_slots)
        return constraints

    def _get_all_classroom_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each classroom can only host one class at a time, and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem.
        """

        def __one_class_at_a_time_constraint(
                classroom: models.Classroom, time_slot: models.TimetableSlot) -> Tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-class-at-a-time' constraint for an individual classroom, and individual timeslot.
            We sum the unsolved class variables relevant to the classroom, and force this to 0 if the teacher has an
            existing commitment at the fixed time slot. Otherwise their sum must be max 1.
            """
            occupied = classroom.check_if_occupied_at_time_slot(slot=time_slot)
            possible_uses = lp.lpSum(
                [self._decision_variables.get(key) for usc in self._inputs.unsolved_classes
                 if (classroom == usc.classroom) and
                 (key := var_key(class_id=usc.class_id, slot_id=time_slot.slot_id)) in self._decision_variables.keys()]
            )
            if occupied:
                constraint = (possible_uses == 0,
                              f"classroom_{classroom.classroom_id}_occupied_at_{time_slot.slot_id}")
            else:
                constraint = (possible_uses <= 1,
                              f"classroom_{classroom.classroom_id}_unoccupied_at_{time_slot.slot_id}")
            return constraint

        constraints = (__one_class_at_a_time_constraint(classroom=classroom, time_slot=time_slot) for
                       classroom in self._inputs.classrooms for time_slot in self._inputs.timetable_slots)
        return constraints

    def _get_all_double_period_fulfillment_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining all constraints on the number of double periods of each class has each week, and returning them
        as a generator.
        """
        def __fulfillment_constraint(unsolved_class: models.UnsolvedClass) -> Tuple[lp.LpConstraint, str]:
            """
            States that the sum of the double period variables for a particular class must equal the number of double
            periods the user has specified.
            """
            variables_sum = lp.lpSum([
                var for key, var in self._double_period_variables.items() if key.class_id == unsolved_class.class_id])
            constraint = (variables_sum == unsolved_class.n_double_periods,
                          f"usc_{unsolved_class.class_id}_must_have_{unsolved_class.n_double_periods}_double_periods")
            return constraint

        constraints = (__fulfillment_constraint(unsolved_class=usc) for usc in self._inputs.unsolved_classes
                       if usc.n_double_periods != 0)
        return constraints

    def _get_all_double_period_dependency_constraints(self) -> itertools.chain:
        """
        Method defining all constraints relating the decision variables and the dependent double period variables.
        We crete 2 separate generators and then chain them together, 1 generator for the first/second slot in each
        double period.
        Note that the core point is that the double period variable >= both decision variables corresponding to the
        same class / time-slot.
        Note also that where a FixedClass occurs, a double period may be created by combining with this existing slot.
        """
        def __dependency_constraint(key: doubles_var_key, is_slot_1: bool) -> Tuple | None:
            """
            Function defining the individual constraint that decision variable corresponding to the first / second slot
            of a double period must be non-zero if the double period variable is non-zero.
            :param key - the key for the double period variables dictionary, which contains info on the class + 2 slots
            :param is_slot_1 - whether we are creating a constraint on slot_1, or on slot_2
            """
            if is_slot_1:
                slot_id = key.slot_1_id
                constraint_name = f"usc_{key.class_id}_double_could_start_at_{slot_id}"
            else:
                slot_id = key.slot_2_id
                constraint_name = f"usc_{key.class_id}_double_could_end_at_{slot_id}"

            try:
                decision_var = self._decision_variables[var_key(class_id=key.class_id, slot_id=slot_id)]
            except KeyError:
                # A FixedClass already occurs at this time, so no need for a constraint
                return None
            double_p_var = self._double_period_variables[key]
            constraint = (decision_var >= double_p_var, constraint_name)
            return constraint

        slot_1_constraints = (
            constraint for key in self._double_period_variables.keys() if
            (constraint := __dependency_constraint(key=key, is_slot_1=True)) is not None)
        slot_2_constraints = (
            constraint for key in self._double_period_variables.keys() if
            (constraint := __dependency_constraint(key=key, is_slot_1=False)) is not None)

        all_constraints = itertools.chain(slot_1_constraints, slot_2_constraints)
        return all_constraints

    def _get_all_no_split_period_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method # TODO
        :return - A generator of pulp constraints and associated names that can be iteratively added to the LpProblem.

        Notes: These constraints to still allow a triple period (since 3 - 2 <= 1), hence the need for the constraint
        below restricting to no two double periods in a day
        """
        # TODO TODO TODO write this method
        # TODO add test for it, also an integration test that adds it
        # TODO - add a test to the solver test scenarios where we are testing this constraint
        # TODO - update the form on the UI which is relevant to this constraint
        def __dependency_constraint() -> Tuple[lp.LpConstraint, str]:
            # TODO: (TOTAL NUMBER PERIODS IN DAY) - (TOTAL NUMBER DOUBLE PERIODS IN DAY) <= 1
            # TODO: NOTE THAT WE STILL NEED THE GET ALL NO DOUBLE PERIOD
            pass


    def _get_all_no_two_double_periods_in_a_day_constraints(self) -> Generator[Tuple[lp.LpConstraint, str], None, None]:
        """
        Method restricting the number of double periods that can be taught for a single class on a single day to 1.
        :return - A generator of pulp constraints and associated names that can be iteratively added to the LpProblem.
        """

        def __no_two_double_periods_in_a_day_constraint(unsolved_class: models.UnsolvedClass,
                                                        day_of_week: models.WeekDay) -> Tuple[lp.LpConstraint, str]:
            """
            States that the given unsolved class can only have one double period on the given day
            :return dp_constraint - a tuple consisting of a pulp constraint and a name for this constraint
            """
            slot_ids_on_day = models.TimetableSlot.get_timeslot_ids_on_given_day(
                school_id=self._inputs.school_id, day_of_week=day_of_week)
            double_periods_on_day = lp.lpSum([  # We only check slot_1_id is in slot_ids, since 1 & 2 are on same day
                var for key, var in self._double_period_variables.items() if
                (key.class_id == unsolved_class.class_id) and (key.slot_1_id in slot_ids_on_day)
            ])
            # TODO - define single period variables
            # TODO - also constrain them as sum(single period vars day x) + sum(double period vars day x) <= 1
            # TODO - we don't actually need the independent double period constraint for this

            dp_constraint = (double_periods_on_day <= 1, f"max_one_{unsolved_class.class_id}_double_day_{day_of_week}")
            return dp_constraint

        relevant_days = {slot.day_of_week for slot in self._inputs.timetable_slots}
        constraints = (__no_two_double_periods_in_a_day_constraint(unsolved_class=usc, day_of_week=day) for
                       usc in self._inputs.unsolved_classes for day in relevant_days)
        return constraints
