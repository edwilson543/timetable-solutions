"""Unit tests for the methods on the TimetableSolverConstraints class"""

# Django imports
from django import test

# Third party imports
from pulp import LpConstraint

# Local application imports
from domain.solver import linear_programming as l_p


class TestSolverConstraints(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json", "unsolved_classes.json"]

    def test_get_all_pupil_constraints(self):
        """
        Test that the correct set of constraints is returned for pupils
        """
        # Set test parameters
        school_access_key = 123456
        data = l_p.TimetableSolverInputs(school_id=school_access_key)
        variables = l_p.TimetableSolverVariables(inputs=data).get_variables()
        constraint_maker = l_p.TimetableSolverConstraints(inputs=data, variables=variables)

        # Execute test unit
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
        # Set test parameters
        school_access_key = 123456
        data = l_p.TimetableSolverInputs(school_id=school_access_key)
        variables = l_p.TimetableSolverVariables(inputs=data).get_variables()
        constraint_maker = l_p.TimetableSolverConstraints(inputs=data, variables=variables)

        # Execute test unit
        teacher_constraints = constraint_maker._get_all_teacher_constraints()

        # Check outcome
        existing_commitment_count = 0  # constraints where the LpAffineExpression must always equal 0
        free_constraint_count = 0  # constraints where the LpAffineExpression could equal 1
        for constraint_tuple in teacher_constraints:
            print(constraint_tuple)
            assert isinstance(constraint_tuple[0], LpConstraint)

            constant = constraint_tuple[0].constant
            if constant == 0:
                existing_commitment_count += 1  # Constraint specifies that the pupil is unavailable at the time
            elif constant == -1:
                free_constraint_count += 1  # Note PuLP takes x <= 1 to become x - 1 <= 0, hence the -1 constant

        assert free_constraint_count + existing_commitment_count == 11 * 35  # = n_pupils * n_timetable_slots
        assert free_constraint_count == 11 * (35 - 5)  # Since we have 5 fixed lunch slots (deducted per pupil)
