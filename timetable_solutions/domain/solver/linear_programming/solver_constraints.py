"""
Module defining the constraints on the timetabling problem
"""

# Standard library imports
import itertools
from typing import Generator

# Third party imports
import pulp as lp

# Local application imports
from data import constants, models
from domain.solver.linear_programming.solver_variables import (
    TimetableSolverVariables,
    doubles_var_key,
    var_key,
)
from domain.solver.solver_input_data import TimetableSolverInputs


class TimetableSolverConstraints:
    """
    Class used to define the constraints for the given timetabling problem, and then add them a LpProblem instance

    The methods are grouped as follows:
        - Entry point method (add_constraints_to_problem)
        - Basic constraints relating to fulfilling timetable criteria, and avoiding clashes
        - Constraints relating to double periods
        - Structural / optional constraints
    """

    def __init__(
        self, inputs: TimetableSolverInputs, variables: TimetableSolverVariables
    ):
        self._inputs = inputs
        self._decision_variables = variables.decision_variables
        self._double_period_variables = variables.double_period_variables

    def add_constraints_to_problem(self, problem: lp.LpProblem) -> None:
        """
        Method to add all constraints to the passed problem - what this class is used for outside this module.
        :param problem - an instance of pulp.LpProblem, which collects constraints/objective and solves
        :return None - since the passed problem will be modified in-place
        """
        # BASIC CONSTRAINTS
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
        # DOUBLE PERIOD CONSTRAINTS
        double_period_fulfillment_constraints = (
            self._get_all_double_period_fulfillment_constraints()
        )
        for constraint in double_period_fulfillment_constraints:
            problem += constraint

        double_period_dependency_constraints = (
            self._get_all_double_period_dependency_constraints()
        )
        for constraint in double_period_dependency_constraints:
            problem += constraint
        # OPTIONAL CONSTRAINTS
        if not self._inputs.solution_specification.allow_split_classes_within_each_day:
            no_split_constraints = self._get_all_no_split_classes_in_a_day_constraints()
            for constraint in no_split_constraints:
                problem += constraint

        if not self._inputs.solution_specification.allow_triple_periods_and_above:
            triple_period_constraints = (
                self._get_all_no_two_doubles_in_a_day_constraints()
            )
            for constraint in triple_period_constraints:
                problem += constraint

    # BASIC CONSTRAINTS ON FULFILLMENT AND CLASH AVOIDANCE
    def _get_all_fulfillment_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each lesson must be taught for the required number of periods.
        """

        def __fulfillment_constraint(
            lesson: models.Lesson,
        ) -> tuple[lp.LpConstraint, str]:
            """
            States that the passed lesson must be taught for the number of required periods, that have not been
            defined by the user.
            """
            n_solver_slots_variable = lp.lpSum(
                [
                    var
                    for key, var in self._decision_variables.items()
                    if key.lesson_id == lesson.lesson_id
                ]
            )
            n_solver_slots_required = lesson.get_n_solver_slots_required()
            constraint = (
                n_solver_slots_variable == n_solver_slots_required,
                f"{lesson.lesson_id}_taught_for_{n_solver_slots_required}_additional_slots",
            )
            return constraint

        constraints = (
            __fulfillment_constraint(lesson) for lesson in self._inputs.lessons
        )
        return constraints

    def _get_all_pupil_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each pupil can only be in one lesson at a time, and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem.
        """

        def __one_place_at_a_slot_constraint(
            pupil: models.Pupil, time_slot: models.TimetableSlot
        ) -> tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-place-at-a-slot' constraint for an individual pupil, and individual timeslot.
            We sum the decision variables relevant to the pupil, and force this to 0 if the pupil has an
            existing commitment at the fixed time slot. Otherwise, their sum must be max 1.

            This is a SLOT based constraint, rather than a TIME based one.
            """
            existing_commitment = pupil.check_if_busy_at_timeslot(slot=time_slot)
            possible_commitments = lp.lpSum(
                [
                    self._decision_variables.get(key)
                    for lesson in pupil.lessons.all()
                    if (
                        key := var_key(
                            lesson_id=lesson.lesson_id, slot_id=time_slot.slot_id
                        )
                    )
                    in self._decision_variables.keys()
                ]
            )
            if existing_commitment:
                constraint = (
                    possible_commitments == 0,
                    f"pupil_{pupil.pupil_id}_unavailable_at_{time_slot.slot_id}",
                )
            else:
                constraint = (
                    possible_commitments <= 1,
                    f"pupil_{pupil.pupil_id}_available_at_{time_slot.slot_id}",
                )
            return constraint

        constraints = (
            __one_place_at_a_slot_constraint(pupil=pupil, time_slot=time_slot)
            for pupil in self._inputs.pupils
            for time_slot in pupil.get_associated_timeslots()
        )
        return constraints

    def _get_all_teacher_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each teacher can only teach one class at a time, and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem.
        """

        def __one_place_at_a_time_constraint(
            teacher: models.Teacher,
            time_slot: models.TimetableSlot,
        ) -> tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-place-at-a-time' constraint for an individual teacher, and individual timeslot.
            We sum the decision variables relevant to the teacher, and force this to 0 if the teacher has an
            existing commitment at the fixed time slot. Otherwise, their sum must be max 1.

            This is a TIME based constraint, rather than a SLOT based one.
            """
            existing_commitment = teacher.check_if_busy_at_time_of_timeslot(
                slot=time_slot
            )
            # Need to constrain against ALL slots clashing with this one
            clashing_slots = self._inputs.timetable_slots.filter_for_clashes(time_slot)

            possible_commitments = lp.lpSum(
                [
                    self._decision_variables.get(key)
                    for lesson in teacher.lessons.all()
                    for clash_slot in clashing_slots
                    if (
                        key := var_key(
                            lesson_id=lesson.lesson_id, slot_id=clash_slot.slot_id
                        )
                    )
                    in self._decision_variables.keys()
                ]
            )

            if existing_commitment:
                constraint = (
                    possible_commitments == 0,
                    f"teacher_{teacher.teacher_id}_unavailable_at_{time_slot.slot_id}",
                )
            else:
                constraint = (
                    possible_commitments <= 1,
                    f"teacher_{teacher.teacher_id}_available_at_{time_slot.slot_id}",
                )
            return constraint

        constraints = (
            __one_place_at_a_time_constraint(teacher=teacher, time_slot=time_slot)
            for teacher in self._inputs.teachers
            for time_slot in self._inputs.timetable_slots
        )
        return constraints

    def _get_all_classroom_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining the constraints that each classroom can only host one class at a time, and returning these as a
        generator that is iterated through once to add each constraint to the LpProblem.
        """

        def __one_class_at_a_time_constraint(
            classroom: models.Classroom, time_slot: models.TimetableSlot
        ) -> tuple[lp.LpConstraint, str]:
            """
            Defines a 'one-class-at-a-time' constraint for an individual classroom, and individual timeslot.
            We sum the decision variables relevant to the classroom, and force this to 0 if the teacher has an
            existing commitment at the fixed time slot. Otherwise, their sum must be max 1.
            """
            occupied = classroom.check_if_occupied_at_time_of_timeslot(slot=time_slot)
            # Need to constrain against ALL slots clashing with this one
            clashing_slots = self._inputs.timetable_slots.filter_for_clashes(time_slot)
            possible_uses = lp.lpSum(
                [
                    self._decision_variables.get(key)
                    for lesson in classroom.lessons.all()
                    for slot in clashing_slots
                    if (
                        key := var_key(lesson_id=lesson.lesson_id, slot_id=slot.slot_id)
                    )
                    in self._decision_variables.keys()
                ]
            )
            if occupied:
                constraint = (
                    possible_uses == 0,
                    f"classroom_{classroom.classroom_id}_occupied_at_{time_slot.slot_id}",
                )
            else:
                constraint = (
                    possible_uses <= 1,
                    f"classroom_{classroom.classroom_id}_unoccupied_at_{time_slot.slot_id}",
                )
            return constraint

        constraints = (
            __one_class_at_a_time_constraint(classroom=classroom, time_slot=time_slot)
            for classroom in self._inputs.classrooms
            for time_slot in self._inputs.timetable_slots
        )
        return constraints

    # DOUBLE PERIOD CONSTRAINTS
    def _get_all_double_period_fulfillment_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining all constraints on the number of double periods of each class has each week, and returning them
        as a generator.
        """

        def __fulfillment_constraint(
            lesson: models.Lesson,
        ) -> tuple[lp.LpConstraint, str]:
            """
            States that the sum of the double period variables for a particular class must equal the number of double
            periods the user has specified.

            Note: A solution involving a user defined lesson, followed by a solver defined lesson in
            consecutive TimeSlots DOES count as a double. This is because there is not a decision variable for the
            user defined lesson, so the double period dependent variable relates to a single decision variable,
            so we have that either both are 0 or both are 1.
            """
            variables_sum = lp.lpSum(
                [
                    var
                    for key, var in self._double_period_variables.items()
                    if key.lesson_id == lesson.lesson_id
                ]
            )

            additional_doubles = lesson.get_n_solver_double_periods_required()
            constraint = (
                variables_sum == additional_doubles,
                f"{lesson.lesson_id}_must_have_{additional_doubles}_additional_double_periods",
            )
            return constraint

        constraints = (
            __fulfillment_constraint(lesson=lesson)
            for lesson in self._inputs.lessons
            if lesson.total_required_double_periods != 0
        )
        return constraints

    def _get_all_double_period_dependency_constraints(self) -> itertools.chain:
        """
        Method defining all constraints relating the decision variables and the dependent double period variables.
        We crete 2 separate generators and then chain them together, 1 generator for the first/second slot in each
        double period.
        Note that the core point is that the double period variable >= both decision variables corresponding to the
        same class / time-slot.
        Note also that a double period IS created by adding a solver defined slot to a user defined slot, which is
        implemented in the second try in the nested try/except blocks below.
        """

        def __dependency_constraint(
            key: doubles_var_key, is_slot_1: bool
        ) -> tuple | None:
            """
            Function defining the individual constraint that decision variable corresponding to the first / second slot
            of a double period must be non-zero if the double period variable is non-zero.
            :param key - the key for the double period variables dictionary, which contains info on the class + 2 slots
            :param is_slot_1 - whether we are creating a constraint on slot_1, or on slot_2
            """
            double_period_var = self._double_period_variables[key]
            # Set a name for the new constraint
            if is_slot_1:
                slot_id = key.slot_1_id
                other_slot_id = key.slot_2_id
                constraint_name = f"{key.lesson_id}_double_could_start_at_{slot_id}"
            else:
                slot_id = key.slot_2_id
                other_slot_id = key.slot_1_id
                constraint_name = f"{key.lesson_id}_double_could_end_at_{slot_id}"
            # Retrieve corresponding decision variable
            try:
                decision_var = self._decision_variables[
                    var_key(lesson_id=key.lesson_id, slot_id=slot_id)
                ]
                constraint = (decision_var >= double_period_var, constraint_name)
            except KeyError:
                # A Lesson already occurs at slot_id
                try:
                    other_decision_var = self._decision_variables[
                        var_key(lesson_id=key.lesson_id, slot_id=other_slot_id)
                    ]
                    constraint = (
                        other_decision_var == double_period_var,
                        f"{key.lesson_id}_occurs_at_{other_slot_id}_if_and_only_if_a_"
                        f"double_period_is_created_with_the_user_defined_slot_at_{slot_id}",
                    )
                except KeyError:
                    # A user defined double period occurs at this time, so no need for a constraint
                    constraint = None
            return constraint

        # Now create and chain two generators, for the first / second slot of each possible double
        slot_1_constraints = (
            constraint
            for key in self._double_period_variables.keys()
            if (constraint := __dependency_constraint(key=key, is_slot_1=True))
            is not None
        )
        slot_2_constraints = (
            constraint
            for key in self._double_period_variables.keys()
            if (constraint := __dependency_constraint(key=key, is_slot_1=False))
            is not None
        )

        all_constraints = itertools.chain(slot_1_constraints, slot_2_constraints)
        return all_constraints

    # STRUCTURAL CONSTRAINTS THAT ONLY GET ADDED DEPENDING ON USER SOLUTION SPECIFICATION
    def _get_all_no_split_classes_in_a_day_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Method defining all constraints to disallow classes to be taught at split times across a single day.
        :return - A generator of pulp constraints and associated names that can be iteratively added to the LpProblem.

        Note: These constraints still allow a stacked triple or quadruple period, hence the need for the constraints
        below restricting the solution to no two double periods in a day (if we do not want triple periods).
        """

        def __no_split_classes_in_a_day_constraint(
            lesson: models.Lesson, day_of_week: constants.Day
        ) -> tuple[lp.LpConstraint, str]:
            """
            We limit: (total number of periods - total number of double periods) to 1 each day, noting that the double
            periods count towards 2 in the total number of periods, and we also count fixed period in the total number.

            :param lesson: the lesson we are disallowing the splitting of within a single day
            :param day_of_week: the day of week we are disallowing the splitting on
            :return: a tuple of the constraint and the name for that constraint
            """
            year_group = lesson.get_associated_year_group()
            slot_ids_on_day = models.TimetableSlot.get_timeslot_ids_on_given_day(
                school_id=self._inputs.school_id,
                day_of_week=day_of_week,
                year_group=year_group,
            )
            # Variables contribution
            periods_on_day = lp.lpSum(
                [
                    var
                    for key, var in self._decision_variables.items()
                    if (key.slot_id in slot_ids_on_day)
                    and (key.lesson_id == lesson.lesson_id)
                ]
            )

            double_periods_on_day = lp.lpSum(
                [  # We only check slot_1_id is in slot_ids, since 1 & 2 are on same day
                    var
                    for key, var in self._double_period_variables.items()
                    if (key.lesson_id == lesson.lesson_id)
                    and (key.slot_1_id in slot_ids_on_day)
                ]
            )
            # Fixed contribution
            existing_singles_on_day = (
                lesson.user_defined_time_slots.get_timeslots_on_given_day(
                    school_id=self._inputs.school_id,
                    day_of_week=day_of_week,
                    year_group=year_group,
                ).count()
            )
            existing_doubles_on_day = (
                lesson.get_user_defined_double_period_count_on_day(
                    day_of_week=day_of_week
                )
            )
            # Since user may have broken the rules, we limit the fixed contribution to 1
            fixed_contribution = min(
                existing_singles_on_day - existing_doubles_on_day, 1
            )

            constraint = (
                periods_on_day - double_periods_on_day + fixed_contribution <= 1,
                f"no_split_{lesson.lesson_id}_classes_on_day_{day_of_week}",
            )
            return constraint

        constraints = (
            __no_split_classes_in_a_day_constraint(lesson=lesson, day_of_week=day)
            for lesson in self._inputs.lessons
            for day in lesson.get_usable_days_of_week()
        )
        return constraints

    def _get_all_no_two_doubles_in_a_day_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Method restricting the number of double periods that can be taught for a single class on a single day to 1.
        :return - A generator of pulp constraints and associated names that can be iteratively added to the LpProblem.

        Note: this also has the effect of preventing triple periods and above
        """

        def __no_two_doubles_in_a_day_constraint(
            lesson: models.Lesson, day_of_week: constants.Day
        ) -> tuple[lp.LpConstraint, str]:
            """
            States that the given lesson can only have one double period on the given day.
            :return dp_constraint - a tuple consisting of a pulp constraint and a name for this constraint
            """
            year_group = lesson.get_associated_year_group()
            slot_ids_on_day = models.TimetableSlot.get_timeslot_ids_on_given_day(
                school_id=self._inputs.school_id,
                day_of_week=day_of_week,
                year_group=year_group,
            )
            solver_doubles_on_day = lp.lpSum(
                [  # We only check slot_1_id is in slot_ids, since 1 & 2 are on same day
                    var
                    for key, var in self._double_period_variables.items()
                    if (key.lesson_id == lesson.lesson_id)
                    and (key.slot_1_id in slot_ids_on_day)
                ]
            )

            existing_doubles_on_day = (
                lesson.get_user_defined_double_period_count_on_day(
                    day_of_week=day_of_week
                )
            )
            existing_doubles_on_day = min(
                existing_doubles_on_day, 1  # Since user may have broken the rules
            )

            dp_constraint = (
                solver_doubles_on_day + existing_doubles_on_day <= 1,
                f"max_one_{lesson.lesson_id}_double_day_{day_of_week}",
            )
            return dp_constraint

        constraints = (
            __no_two_doubles_in_a_day_constraint(lesson=lesson, day_of_week=day)
            for lesson in self._inputs.lessons
            for day in lesson.get_usable_days_of_week()
        )
        return constraints
