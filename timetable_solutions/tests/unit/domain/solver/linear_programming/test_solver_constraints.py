"""Unit tests for the methods on the TimetableSolverConstraints class"""

# Django imports
from django import test

# Third party imports
from pulp import LpConstraint

# Local application imports
from domain import solver as slvr


def get_constraint_maker() -> slvr.TimetableSolverConstraints:
    """
    Method used to instantiate the 'maker' of pulp constraints. Would use pytest fixtures, but this does not work
    since the test class subclasses the Django TestCase.
    Note that we include a default solution specification also within this method.
    """
    school_access_key = 123456
    spec = slvr.SolutionSpecification(
        allow_split_classes_within_each_day=True,
        allow_triple_periods_and_above=True,
    )
    data = slvr.TimetableSolverInputs(
        school_id=school_access_key, solution_specification=spec
    )
    variables = slvr.TimetableSolverVariables(inputs=data)
    constraint_maker = slvr.TimetableSolverConstraints(inputs=data, variables=variables)
    return constraint_maker


class TestSolverConstraints(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_without_solution.json",
    ]

    def test_get_all_fulfillment_constraints(self):
        """
        Test that the correct set of fulfillment constraints is returned for all the lessons.
        We expect one constraint per lesson.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        constraints = constraint_maker._get_all_fulfillment_constraints()

        # Check outcome
        constraint_count = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            # Since each decision variable is included in the sum
            assert len(constraint) == 30
            # Even if fixed lessons occupy the slots, should still be some free vars
            assert constraint.constant < 0
            constraint_count += 1
        assert constraint_count == 12

    def test_get_all_pupil_constraints(self):
        """
        Test that the correct set of constraints is returned for pupils
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        pup_constraints = constraint_maker._get_all_pupil_constraints()

        # Check outcome

        # constraints where the LpAffineExpression could equal 1
        constraint_count = 0

        for constraint_tuple in pup_constraints:
            assert isinstance(constraint_tuple[0], LpConstraint)
            constraint_count += 1

        # = n_pupils * n_timetable_slots
        assert constraint_count == 6 * 30

    def test_get_all_teacher_constraints(self):
        """
        Test that the correct set of constraints is returned for teachers
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        teacher_constraints = constraint_maker._get_all_teacher_constraints()

        # Check outcome
        constraint_count = 0

        for constraint_tuple in teacher_constraints:
            assert isinstance(constraint_tuple[0], LpConstraint)
            constraint_count += 1

            # = n_teachers * n_timetable_slots
        assert constraint_count == 11 * 30

    def test_get_all_classroom_constraints(self):
        """
        Test that the correct set of constraints is returned for classrooms
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        classroom_constraints = constraint_maker._get_all_classroom_constraints()

        # Check outcome
        constraint_count = 0

        for constraint_tuple in classroom_constraints:
            assert isinstance(constraint_tuple[0], LpConstraint)
            constraint_count += 1

        # = n_classrooms * n_timetable_slots
        assert constraint_count == 12 * 30

    def test_get_all_double_period_fulfillment_constraints(self):
        """
        Test that the correct set of constraints on the number of double periods is returned.
        We expect one constraint per lesson class.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        dp_fulfillment_constraints = (
            constraint_maker._get_all_double_period_fulfillment_constraints()
        )

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in dp_fulfillment_constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            # Since each double-period variable is included in the sum
            # And we have 5 days * 4 double period options
            assert len(constraint) == 5 * 4
            constraint_count += 1
        assert constraint_count == 12

    def test_get_all_double_period_dependency_constraints(self):
        """
        Test that the correct set of constraints is returned linking the decision variables and the double period
        variables
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        dependency_constraints = (
            constraint_maker._get_all_double_period_dependency_constraints()
        )

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in dependency_constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            assert len(constraint) == 2
            constraint_count += 1
        # Note that we have 12 lessons; 6 double options / day / class; 5 days; 2 related decision variables
        assert constraint_count == 12 * 4 * 5 * 2

    def test_get_all_no_two_doubles_in_a_day_constraint(self):
        """
        Test that the correct set of constraints is returned limiting the number of double periods that can take place
        on one day to 1.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        constraints = constraint_maker._get_all_no_two_doubles_in_a_day_constraints()

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            # Can have 2 double periods before, and 2 doubler periods after lunch
            assert len(constraint) == 4
            assert constraint.constant == -1  # 1 Double period per day
            constraint_count += 1
        assert constraint_count == 5 * 12  # number days * number lessons


class TestSolverConstraintsWithExtraYear(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_without_solution.json",
        "extra-year.json",
    ]

    def test_get_all_fulfillment_constraints(self):
        """
        Test that the correct set of fulfillment constraints is returned for all the lessons,
        when some year groups have different timetables.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        constraints = constraint_maker._get_all_fulfillment_constraints()

        # Check outcome
        constraint_count = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            # Constant less than zero indicates that there is something to solver
            assert constraint.constant < 0

            if "extra_year" in str(constraint):
                # Extra year only has 2 slots & deision variables, so this is the constraint length
                assert len(constraint) == 2
            else:
                # Each decision variable for the 30 slots is included in the sum
                assert len(constraint) == 30

            constraint_count += 1

        assert constraint_count == 14

    def test_get_all_pupil_constraints_extra_year(self):
        """
        Test that the correct set of constraints is returned for pupils,
        when some year groups have different timetables.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        pup_constraints = constraint_maker._get_all_pupil_constraints()

        # Check outcome
        extra_year_constraints = 0
        other_constraints = 0

        for constraint_tuple in pup_constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)

            if "extra_year" in str(constraint):
                # All pupils are free, so each constraint is just: decision var - 1 <= 0
                assert len(constraint) == 1
                assert constraint.constant == -1
                extra_year_constraints += 1

            else:
                other_constraints += 1

        # These should just match n_pupils * n_slots
        assert extra_year_constraints == 2 * 2
        assert other_constraints == 6 * 30

    def test_get_all_teacher_constraints_extra_year(self):
        """
        Test that the correct set of constraints is returned for teachers,
        when some year groups have different timetables.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        teacher_constraints = constraint_maker._get_all_teacher_constraints()

        # Check outcome
        n_constraints = 0

        for constraint_tuple in teacher_constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)

            if "extra_year" in str(constraint):
                # Each teacher has just one lesson, so each constraint is just: decision var - 1 <= 0
                assert len(constraint) == 1
                assert constraint.constant == -1

            n_constraints += 1

        # These should just match number of teachers * slots
        # (extra year teachers + other teachers) * (extra year slots + other slots)
        assert n_constraints == (2 + 11) * (2 + 30)

    def test_get_all_classroom_constraints_extra_year(self):
        """
        Test that the correct set of constraints is returned for classrooms,
        when some year groups have different timetables.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        teacher_constraints = constraint_maker._get_all_classroom_constraints()

        # Check outcome
        n_constraints = 0

        for constraint_tuple in teacher_constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)

            if "extra_year" in str(constraint):
                # Each classroom has just one lesson, so each constraint is just: decision var - 1 <= 0
                assert len(constraint) == 1
                assert constraint.constant == -1

            n_constraints += 1

        # These should just match number of classrooms * slots
        # (extra year classrooms + other classrooms) * (extra year slots + other slots)
        assert n_constraints == (2 + 12) * (2 + 30)

    def test_get_all_no_split_classes_within_day_constraints_constraints(self):
        """
        Test that the correct set of constraints is returned preventing split periods,
        when some year groups have different timetables.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        constraints = constraint_maker._get_all_no_split_classes_in_a_day_constraints()

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]

            if "extra_year" in str(constraint):
                # Here we have slot 1 + slot 2 - double at slot 1&2  <= 1
                assert len(constraint) == 3
                assert constraint.constant == -1

            else:
                assert isinstance(constraint, LpConstraint)
                # We have 6 decision variables and 4 double period variables in the mix
                assert len(constraint) == 10
                assert constraint.constant == -1

            constraint_count += 1

        assert constraint_count == (5 * 12) + (1 * 2)  # number days * number lessons

    def test_get_all_no_two_doubles_in_a_day_constraint(self):
        """
        Test that the correct set of constraints is returned limiting the number of double periods that can take place
        on one day to 1, when some year groups have different timetables.
        """
        # Execute test unit
        constraint_maker = get_constraint_maker()
        constraints = constraint_maker._get_all_no_two_doubles_in_a_day_constraints()

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]

            if "extra_year" in str(constraint):
                assert isinstance(constraint, LpConstraint)
                # Just saying double period at slots 1 & 2 <= 1
                assert len(constraint) == 1
                assert constraint.constant == -1  # 1 Double period per day

            else:

                assert isinstance(constraint, LpConstraint)
                # 2 triplets of consecutive slots, so 4 possible double periods
                assert len(constraint) == 4
                assert constraint.constant == -1  # 1 Double period per day

            constraint_count += 1

        assert constraint_count == (5 * 12) + (1 * 2)  # number days * number lessons
