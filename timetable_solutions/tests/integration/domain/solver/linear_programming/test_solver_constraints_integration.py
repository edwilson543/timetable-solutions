"""Integration test for the entry-point method on the TimetableSolverConstraints class"""

# Django imports
from django import test

# Third party imports
import pulp as lp

# Local application imports
from domain import solver as slvr


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

    def test_add_all_constraints_to_problem(self):
        """
        Test that the full set of constraints necessary to specify the timetabling problem is added to the problem as
        expected.

        Note that we set the solution specification such that all constraints get added.
        """
        # Set test parameters
        school_access_key = 123456
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=False,
            allow_triple_periods_and_above=False,
        )
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        variables = slvr.TimetableSolverVariables(inputs=data)
        constraint_maker = slvr.TimetableSolverConstraints(
            inputs=data, variables=variables
        )

        dummy_problem = (
            lp.LpProblem()
        )  # In real life, will be the LpProblem subclass carried by TimetableSolver

        # Execute test unit
        constraint_maker.add_constraints_to_problem(problem=dummy_problem)

        # Check outcome - note the dummy_problem is modified in-place
        constraints = dummy_problem.constraints

        # fulfillment + pupil + teacher + classroom + double period fulfillment + double period dependency
        fulfillment_pupil_teacher_classroom = 12 + (6 * 35) + (11 * 35) + (12 * 35)
        double_period_fulfillment_dependency = 12 + (12 * 30 * 2)
        no_split_no_triples = (12 * 5) + (12 * 5)
        assert (
            len(constraints)
            == fulfillment_pupil_teacher_classroom
            + double_period_fulfillment_dependency
            + no_split_no_triples
        )
