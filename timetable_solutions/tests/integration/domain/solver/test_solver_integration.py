"""Integration tests for the TimetableSolver class"""

# Django imports
from django import test

# Third party imports
import pulp as lp

# Local application imports
from domain.solver import linear_programming as l_p


class TestSolver(test.TestCase):
    """
    Test that the solver can produce a solution for the default fixtures.
    These fixtures are not contrived to produce a specific solution, so we do not test what the solution actually is.
    """

    fixtures = ["user_school_profile.json", "solver_pupils.json"]

    def test_add_all_constraints_to_problem(self):
        """
        Test that the full set of constraints necessary to specify the timetabling problem is added to the problem
        """
        # Set test parameters
        school_access_key = 123456
        data = l_p.TimetableSolverInputs(school_id=school_access_key)
        solver = l_p.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome - i.e. that a solution has been found
        self.assertTrue(lp.LpStatus[solver.problem.status], "Optimal")


class TestSolverScenarioSolutions(test.TestCase):
    """
    Tests where we are after a specific solution
    """

    fixtures = ["user_school_profile.json", "solver_pupils.json"]

    def test_add_all_constraints_to_problem(self):
        """
        Test that the full set of constraints necessary to specify the timetabling problem is added to the problem
        """
        # Set test parameters
        school_access_key = 123456
        # data = l_p.TimetableSolverInputs(school_id=school_access_key)
        # solver = l_p.TimetableSolver(input_data=data)
        #
        # # Execute test unit
        # solver.solve()
