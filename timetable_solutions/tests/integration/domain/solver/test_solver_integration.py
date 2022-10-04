"""Integration tests for the TimetableSolver class"""

# Django imports
from django import test

# Third party imports
import pulp as lp

# Local application imports
from domain import solver as slvr


class TestSolver(test.TestCase):
    """
    Test that the solver can produce a solution for the default fixtures.
    These fixtures are not contrived to produce a specific solution, so we do not test what the solution actually is.
    """
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json", "unsolved_classes.json"]

    def test_solver_finds_a_solution_for_default_fixtures(self):
        """
        Test that the full set of constraints necessary to specify the timetabling problem is added to the problem
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome - i.e. that a solution has been found
        assert lp.LpStatus[solver.problem.status] == "Optimal"


class TestSolverScenarioSolutions(test.TestCase):
    """
    Tests where we are after a specific solution
    """

    fixtures = ["user_school_profile.json", "test_scenario_1.json"]

    def test_solver_solution_test_scenario_1(self):
        """
        Test scenario 1 essentially represents a test of the fulfillment constraint. There are 2 pupils / teachers /
        timeslots / fixed classes / unsolved classes. Each fixed class occupies one of the slots, and the unsolved class
        states 2 slots must be used, so the solution is just to occupy the remaining slot, for each class.
        """
        # Set test parameters
        school_access_key = 123456
        data = slvr.TimetableSolverInputs(school_id=school_access_key)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables) == 2  # Only one option for where each unsolved class' remaining slots could go
        assert solver.variables[slvr.var_key(class_id="YEAR_ONE_MATHS_A", slot_id=2)].varValue == 1
        assert solver.variables[slvr.var_key(class_id="YEAR_ONE_MATHS_B", slot_id=1)].varValue == 1
