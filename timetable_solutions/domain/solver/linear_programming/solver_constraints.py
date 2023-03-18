"""
Declares the class handling timetable constraints.
"""

# Standard library imports
from typing import Generator

# Third party imports
import pulp as lp

# Local application imports
from data import constants, models
from domain.solver.filters import clashes
from domain.solver.linear_programming.solver_variables import (
    TimetableSolverVariables,
    doubles_var_key,
    var_key,
)
from domain.solver.queries import classroom as classroom_queries
from domain.solver.queries import pupil as pupil_queries
from domain.solver.queries import teacher as teacher_queries
from domain.solver.solver_input_data import TimetableSolverInputs


class TimetableSolverConstraints:
    """
    Define the constraints on a school's timetabling problem.

    The constraints are grouped as follows:
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
        Add all relevant constraints to the passed problem.

        :param problem: A timetabling problem for a single school.
        :return None: The problem is mutated.
        """
        # Fulfillment
        for constraint in self._get_all_fulfillment_constraints():
            problem += constraint

        # One place at a time constraints
        for constraint in self._get_all_pupil_constraints():
            problem += constraint

        for constraint in self._get_all_teacher_constraints():
            problem += constraint

        for constraint in self._get_all_classroom_constraints():
            problem += constraint

        # Double period constraints
        for constraint in self._get_all_double_period_fulfillment_constraints():
            problem += constraint

        for constraint in self._get_all_double_period_dependency_constraints():
            problem += constraint

        # Structural constraints
        if not self._inputs.solution_specification.allow_split_lessons_within_each_day:
            for constraint in self._get_all_no_split_lessons_in_a_day_constraints():
                problem += constraint

        if not self._inputs.solution_specification.allow_triple_periods_and_above:
            for constraint in self._get_all_no_two_doubles_in_a_day_constraints():
                problem += constraint

    # --------------------
    # Fulfillment constraints
    # --------------------

    def _get_all_fulfillment_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Ensure every lesson is assigned the required number of slots.
        """

        def __fulfillment_constraint(
            lesson: models.Lesson,
        ) -> tuple[lp.LpConstraint, str]:
            """
            Ensure this lesson is assigned the required number of slots.
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

        yield from (__fulfillment_constraint(lesson) for lesson in self._inputs.lessons)

    # --------------------
    # One place at a time constraints
    # --------------------

    def _get_all_pupil_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Ensure every pupil is only assigned one lesson at a time.
        """

        def __one_place_at_a_slot_constraint(
            pupil: models.Pupil, time_slot: models.TimetableSlot
        ) -> tuple[lp.LpConstraint, str]:
            """
            Ensure this pupil is only assigned one lesson at the given time slot.

            Equation: sum the decision variables relevant to the pupil at the time slot.
            Force to 0 if they have an existing lesson at any of the times.
            Otherwise, their sum must be at most 1.
            """
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

            existing_commitment = pupil_queries.check_if_pupil_busy_at_time(
                pupil,
                starts_at=time_slot.starts_at,
                ends_at=time_slot.ends_at,
                day_of_week=time_slot.day_of_week,
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

        yield from (
            __one_place_at_a_slot_constraint(pupil=pupil, time_slot=time_slot)
            for pupil in self._inputs.pupils
            for time_slot in pupil.get_associated_timeslots()
        )

    def _get_all_teacher_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Ensure every teacher is only assigned one lesson at a time.
        """

        def __one_place_at_a_time_constraint(
            teacher: models.Teacher,
            time_slot: models.TimetableSlot,
        ) -> tuple[lp.LpConstraint, str]:
            """
            Ensure this teacher is only assigned one lesson at the time spanned by the given time slot.

            Equation: sum the decision variables relevant to the teacher at the time
            of the time slot. Force to 0 if they have an existing lesson at any of the times.
            Otherwise, their sum must be at most 1.
            """
            # Need to constrain against ALL slots clashing with this one,
            # since the teacher can only be utilised for ONE of these slots
            clashing_slots = clashes.filter_queryset_for_clashes(
                queryset=self._inputs.timetable_slots,
                time_of_week=clashes.TimeOfWeek.from_slot(slot=time_slot),
            )

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

            existing_commitment = teacher_queries.check_if_teacher_busy_at_time(
                teacher,
                starts_at=time_slot.starts_at,
                ends_at=time_slot.ends_at,
                day_of_week=time_slot.day_of_week,
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

        yield from (
            __one_place_at_a_time_constraint(teacher=teacher, time_slot=time_slot)
            for teacher in self._inputs.teachers
            for time_slot in self._inputs.timetable_slots
        )

    def _get_all_classroom_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Ensure every classroom is only assigned one lesson at a time.
        """

        def __one_class_at_a_time_constraint(
            classroom: models.Classroom, time_slot: models.TimetableSlot
        ) -> tuple[lp.LpConstraint, str]:
            """
            Ensure this classroom is only assigned one lesson at the time spanned by the given time slot.

            Equation: sum the decision variables relevant to the classroom at the time
            of the time slot. Force to 0 if it has an existing lesson at any of the times.
            Otherwise, their sum must be at most 1.
            """
            # Need to constrain against ALL slots clashing with this one
            # since the teacher can only be utilised for ONE of these slots
            clashing_slots = clashes.filter_queryset_for_clashes(
                queryset=self._inputs.timetable_slots,
                time_of_week=clashes.TimeOfWeek.from_slot(slot=time_slot),
            )
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

            existing_use = classroom_queries.check_if_classroom_occupied_at_time(
                classroom,
                starts_at=time_slot.starts_at,
                ends_at=time_slot.ends_at,
                day_of_week=time_slot.day_of_week,
            )
            if existing_use:
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

        yield from (
            __one_class_at_a_time_constraint(classroom=classroom, time_slot=time_slot)
            for classroom in self._inputs.classrooms
            for time_slot in self._inputs.timetable_slots
        )

    # --------------------
    # Double period constraints
    # --------------------

    def _get_all_double_period_fulfillment_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Ensure the required number of double periods for each lesson is fulfilled.
        """

        def __fulfillment_constraint(
            lesson: models.Lesson,
        ) -> tuple[lp.LpConstraint, str]:
            """
            Ensure the required number of double periods for a single lesson is fulfilled.

            Equation: Sum of the double period variables for this lesson must equal the
            number of additional double periods the user has specified. The number of additional
            periods required will just be zero if the user has defined them all.

            Note: A solution involving a user defined lesson, followed by a solver defined lesson in
            consecutive TimeSlots IS counted as a double. This is because there is not a decision
            variable for the user defined lesson, so the double period dependent variable relates to
            a single decision variable, so we have that either both are 0 or both are 1.
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

        yield from (
            __fulfillment_constraint(lesson=lesson)
            for lesson in self._inputs.lessons
            if lesson.total_required_double_periods != 0
        )

    def _get_all_double_period_dependency_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Relate the dependent double period variables to the decision variables.

        A double period can happen if and only if the decision variables for each of the
        covered slots equal 1.

        Note that a double period created by adding a solver defined slot to a user defined slot,
        is counted.
        """

        def __dependency_constraint(
            key: doubles_var_key, is_slot_1: bool
        ) -> tuple[lp.LpConstraint, str] | None:
            """
            Relate a single double period variable to the decision variables for its first and second slot.

            :param key - the key for the double period variables dictionary, which contains info on the class + 2 slots
            :param is_slot_1 - whether we are creating a constraint on slot_1, or on slot_2.
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

        # Yield a constraint for the first and second slot of each possible double
        yield from (
            constraint
            for key in self._double_period_variables.keys()
            if (constraint := __dependency_constraint(key=key, is_slot_1=True))
            is not None
        )
        yield from (
            constraint
            for key in self._double_period_variables.keys()
            if (constraint := __dependency_constraint(key=key, is_slot_1=False))
            is not None
        )

    # --------------------
    # Structural constraints
    # These get added depending on the solution specification
    # --------------------

    def _get_all_no_split_lessons_in_a_day_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Disallow all lessons being taught at split times in a single day.

        Note: These constraints still allow a stacked triple or quadruple period, hence the need for the constraints
        below restricting the solution to no two double periods in a day (if we do not want triple periods).
        """

        def __no_split_lessons_in_a_day_constraint(
            lesson: models.Lesson, day_of_week: constants.Day
        ) -> tuple[lp.LpConstraint, str]:
            """
            Disallow a single lesson being taught at split times in a single day.

            Equation: (total number of periods - total number of double periods) <= 1, every day.
            Note that the double periods count towards 2 in the total number of periods,
            and we also count user defined slots in the total number.

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

            # Checking slot_1_id is in slot_ids is sufficient, since 1 & 2 are on same day
            double_periods_on_day = lp.lpSum(
                [
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

        yield from (
            __no_split_lessons_in_a_day_constraint(lesson=lesson, day_of_week=day)
            for lesson in self._inputs.lessons
            for day in lesson.get_usable_days_of_week()
        )

    def _get_all_no_two_doubles_in_a_day_constraints(
        self,
    ) -> Generator[tuple[lp.LpConstraint, str], None, None]:
        """
        Restrict the number of double periods each day to 1, for all lessons.

        Note: this has the effect of preventing triple periods and above, since a triple
        period is implemented as two doubles.
        """

        def __no_two_doubles_in_a_day_constraint(
            lesson: models.Lesson, day_of_week: constants.Day
        ) -> tuple[lp.LpConstraint, str]:
            """
            Restrict the number of double periods on a single day to 1, for a single lesson.
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

        yield from (
            __no_two_doubles_in_a_day_constraint(lesson=lesson, day_of_week=day)
            for lesson in self._inputs.lessons
            for day in lesson.get_usable_days_of_week()
        )
