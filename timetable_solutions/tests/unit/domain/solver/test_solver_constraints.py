"""Unit tests for the methods on the TimetableSolverConstraints class"""

# Standard library imports
from functools import lru_cache

# Django imports
from django import test

# Third party imports
from pulp import LpConstraint

# Local application imports
from domain import solver as slvr


class TestSolverConstraints(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json", "unsolved_classes.json"]

    @staticmethod
    @lru_cache(maxsize=1)
    def get_constraint_maker() -> slvr.TimetableSolverConstraints:
        """
        Method used to instantiate the 'maker' of pulp constraints. Would use pytest fixture, but this does not work
        since the test class subclasses the Django TestCase
        """
        school_access_key = 123456
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        variables = slvr.TimetableSolverVariables(inputs=data)
        constraint_maker = slvr.TimetableSolverConstraints(inputs=data, variables=variables)
        return constraint_maker

    def test_get_all_fulfillment_constraints(self):
        """
        Test that the correct set of fulfillment constraints is returned for all the unsolved classes.
        We expect one constraint oer unsolved class.
        """
        # Execute test unit
        constraint_maker = self.get_constraint_maker()
        constraints = constraint_maker._get_all_fulfillment_constraints()

        # Check outcome
        constraint_count = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            assert len(constraint) == 35  # Since each decision variable is included in the sum
            assert constraint.constant < 0  # Even if fixed classes occupy the slots, should still be some free vars
            constraint_count += 1
        assert constraint_count == 12

    def test_get_all_pupil_constraints(self):
        """
        Test that the correct set of constraints is returned for pupils
        """
        # Execute test unit
        constraint_maker = self.get_constraint_maker()
        pup_constraints = constraint_maker._get_all_pupil_constraints()

        # Check outcome
        existing_commitment_count = 0  # constraints where the LpAffineExpression must always equal 0
        free_constraint_count = 0  # constraints where the LpAffineExpression could equal 1
        for constraint_tuple in pup_constraints:
            assert isinstance(constraint_tuple[0], LpConstraint)

            constant = constraint_tuple[0].constant
            if constant == 0:
                existing_commitment_count += 1  # Constraint specifies that the pupil is unavailable at the time
            elif constant == -1:
                free_constraint_count += 1  # Note PuLP takes x <= 1 to become x - 1 <= 0, hence the -1 constant

        assert free_constraint_count + existing_commitment_count == 6 * 35  # = n_pupils * n_timetable_slots
        assert free_constraint_count == 6 * (35 - 5)  # Since we have 5 fixed lunch slots (deducted per pupil)

    def test_get_all_teacher_constraints(self):
        """
        Test that the correct set of constraints is returned for teachers
        """
        # Execute test unit
        constraint_maker = self.get_constraint_maker()
        teacher_constraints = constraint_maker._get_all_teacher_constraints()

        # Check outcome
        existing_commitment_count = 0  # constraints where the LpAffineExpression must always equal 0
        free_constraint_count = 0  # constraints where the LpAffineExpression could equal 1
        for constraint_tuple in teacher_constraints:
            assert isinstance(constraint_tuple[0], LpConstraint)

            constant = constraint_tuple[0].constant
            if constant == 0:
                existing_commitment_count += 1  # Constraint specifies that the teacher is unavailable at the time
            elif constant == -1:
                free_constraint_count += 1  # Note PuLP takes x <= 1 to become x - 1 <= 0, hence the -1 constant

        assert free_constraint_count + existing_commitment_count == 11 * 35  # = n_teachers * n_timetable_slots
        assert free_constraint_count == 11 * (35 - 5)  # Since we have 5 fixed lunch slots (deducted per teacher)

    def test_get_all_classroom_constraints(self):
        """
        Test that the correct set of constraints is returned for classrooms
        """
        # Execute test unit
        constraint_maker = self.get_constraint_maker()
        classroom_constraints = constraint_maker._get_all_classroom_constraints()

        # Check outcome
        existing_occupied_count = 0  # constraints where the LpAffineExpression must always equal 0
        free_constraint_count = 0  # constraints where the LpAffineExpression could equal 1
        for constraint_tuple in classroom_constraints:
            assert isinstance(constraint_tuple[0], LpConstraint)

            constant = constraint_tuple[0].constant
            if constant == 0:
                existing_occupied_count += 1  # Constraint specifies that the classroom is occupied at the time
            elif constant == -1:
                free_constraint_count += 1  # Note PuLP takes x <= 1 to become x - 1 <= 0, hence the -1 constant

        assert free_constraint_count + existing_occupied_count == 12 * 35  # = n_classrooms * n_timetable_slots
        assert free_constraint_count == 12 * 35  # No lunch hall in fixture for now...

    def test_get_all_double_period_fulfillment_constraints(self):
        """
        Test that the correct set of constraints on the number of double periods is returned.
        We expect one constraint per unsolved class.
        """
        # Execute test unit
        constraint_maker = self.get_constraint_maker()
        dp_fulfillment_constraints = constraint_maker._get_all_double_period_fulfillment_constraints()

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in dp_fulfillment_constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            assert len(constraint) == 30  # Since each double-period variable is included in the sum
            constraint_count += 1
        assert constraint_count == 12

    def test_get_all_double_period_dependency_constraints(self):
        """
        Test that the correct set of constraints is returned linking the decision variables and the double period
        variables
        """
        # Execute test unit
        constraint_maker = self.get_constraint_maker()
        dependency_constraints = constraint_maker._get_all_double_period_dependency_constraints()

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in dependency_constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            assert len(constraint) == 2
            constraint_count += 1
        # Note that we haveL 12 unsolved classes; 6 double options / day / class; 5 days; 2 related decision variables
        assert constraint_count == 12 * 6 * 5 * 2

    def test_get_all_no_split_classes_within_day_constraints_constraints(self):
        """
        Test that the correct set of constraints is returned preventing split periods.
        """
        # Execute test unit
        constraint_maker = self.get_constraint_maker()
        constraints = constraint_maker._get_all_no_split_classes_within_day_constraints()

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            assert len(constraint) == 13  # Since we have 7 decision variables and 6 double period variables in the mix
            assert constraint.constant == - 1  # 1 Double period per day
            constraint_count += 1
        assert constraint_count == 5 * 12  # number days * number unsolved classes

    def test_get_all_no_triple_periods_and_above_constraints(self):
        """
        Test that the correct set of constraints is returned limiting the number of double periods that can take place
        on one day to 1.
        """
        # Execute test unit
        constraint_maker = self.get_constraint_maker()
        constraints = constraint_maker._get_all_no_triple_periods_and_above_constraints()

        # Check the outcome
        constraint_count = 0
        for constraint_tuple in constraints:
            constraint = constraint_tuple[0]
            assert isinstance(constraint, LpConstraint)
            assert len(constraint) == 6  # Since there are 6 double periods that can happen in each day
            assert constraint.constant == - 1  # 1 Double period per day
            constraint_count += 1
        assert constraint_count == 5 * 12  # number days * number unsolved classes
