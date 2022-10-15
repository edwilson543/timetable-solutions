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
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=False,
                                          allow_triple_periods_and_above=False)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome - i.e. that a solution has been found
        assert lp.LpStatus[solver.problem.status] == "Optimal"


class TestSolverScenarioSolutions(test.TestCase):
    """
    Tests where we are after a specific solution
    """

    fixtures = ["test_scenario_1.json", "test_scenario_2.json", "test_scenario_3.json", "test_scenario_4.json",
                "test_scenario_5.json", "test_scenario_6.json", "test_scenario_8.json"]

    # Note that test scenarios 7 and above do not use this solution spec
    solution_spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                               allow_triple_periods_and_above=True)

    # TESTS WHERE A BASIC CONSTRAINT IS LIMITING
    def test_solver_solution_test_scenario_1(self):
        """
        Test scenario targeted at the fulfillment constraint.
        There are 2 pupils / teachers / timeslots / fixed classes / unsolved classes. Each fixed class occupies one of
        the slots, and the unsolved class states 2 slots must be used, so the solution is just to occupy the remaining
        slot, for each class.
        """
        # Set test parameters
        school_access_key = 111111
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 2  # 1 option where each of 2 class' remaining slot could go
        assert solver.variables.decision_variables[slvr.var_key(class_id="YEAR_ONE_MATHS_A", slot_id=2)].varValue == 1
        assert solver.variables.decision_variables[slvr.var_key(class_id="YEAR_ONE_MATHS_B", slot_id=1)].varValue == 1

    def test_solver_solution_test_scenario_2(self):
        """
        Test scenario targeted at the pupil one-place-at-a-time constraint.
        Test scenario 2 represents a test of the pupil one-place-at-a-time constraint. There is one pupil, who must
        go to 2 classes. There are 2 time slots. There are no fixed classes, or other constraints.
        """
        # Set test parameters
        school_access_key = 222222
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 4  # Either class could be taught in either slot
        # We test now that the sufficient classes take place, and not simultaneously
        c1_t1 = solver.variables.decision_variables[slvr.var_key(class_id="MATHS", slot_id=1)].varValue
        c1_t2 = solver.variables.decision_variables[slvr.var_key(class_id="MATHS", slot_id=2)].varValue
        c2_t1 = solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue
        c2_t2 = solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue
        assert c1_t1 + c1_t2 == 1
        assert c2_t1 + c2_t2 == 1

    def test_solver_solution_test_scenario_3(self):
        """
        Test scenario targeted at the teacher one-place-at-a-time constraint.
        A teacher must take 2 classes, one of which is fixed and one of which is unsolved. Both use 1 slot, and there
        are 2 possible time slots
        """
        # Set test parameters
        school_access_key = 333333
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 2  # Unsolved class' 1 slot could go in either time slot
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue == 0  # Busy
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 1

    def test_solver_solution_test_scenario_4(self):
        """
        Test scenario targeted at the classroom one-class-at-a-time constraint.
        Two classes share a classroom, but neither pupils nor teachers. One must take place at a certain time, leaving
        only one option for the remaining class.
        """
        # Set test parameters
        school_access_key = 444444
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 2  # Unsolved class' 1 slot could go in either time slot
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue == 0  # Busy
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 1

    # TESTS WHERE A DOUBLE PERIOD CONSTRAINT IS LIMITING
    def test_solver_solution_test_scenario_5(self):
        """
        Test scenario targeted at the double period fulfillment and dependency constraints.
        There are 3 timeslots, and one UnsolvedClass that must have a total of 2 slots, which must be a double period.
        Only 2 of the 3 timeslots are consecutive, so we must have the doubler period during these slots.
        """
        # Set test parameters
        school_access_key = 555555
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 3  # 1 unsolved class must be taught in 2 / 3 time slots

        # The double period is slots 2 & 3
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 1
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=3)].varValue == 1

    def test_solver_solution_test_scenario_6(self):
        """
        Test scenario targeted at the double period fulfillment and dependency constraints, in the particular instance
        where a FixedClass comes into play.
        There are 4 timeslots, as 2 pairs of consecutive slots.
        There is one UnsolvedClass that must have a total of 2 slots, which must be a double period, and
        a corresponding FixedClass with 1 defined slot. Therefore the solution is to attach a second slot to the
        already defined slot, making the double.
        """
        # Set test parameters
        school_access_key = 666666
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 3  # 4 slots, 1 class, but one variable gets stripped

        # The fixed class is at slot 4, slots (1 & 2) and (3 & 4) are the consecutive pairs
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=3)].varValue == 1

    # TODO TEST SCENARIO 10 CHECKING THAT FIXED CLASS COUNTS AS DOUBLE PERIOD

    # TESTS WHERE A STRUCTURAL, OPTIONAL CONSTRAINT IS LIMITING
    def test_solver_solution_test_scenario_8(self):
        """
        Test scenario targeted at the no split classes constraints.
        There are 3 timeslots, 2 on Monday and 1 on Tuesday. There is 1 UnsolvedClass, requiring 2 periods and exatly 0
        double periods. One of the periods has already been fixed for the Monday, so by the no split classes constraint,
        the remaining class has to be taught on Tuesday
        """
        # Set test parameters
        school_access_key = 888888
        spec = slvr.SolutionSpecification(allow_triple_periods_and_above=True,  # True but irrelevant
                                          allow_split_classes_within_each_day=False)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 2  # 3 slots, 1 class, but one variable gets stripped

        # Slot_id 3 represents the individual slot on the Tuesday where we want the class to happen
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=3)].varValue == 1

    # TODO TEST SCENARIO 8 USING THE NO TRIPLES CONSTRAINT

    # TODO TEST SCENARIO 9 USING BOTH NO SPLIT AND NO TRIPLES



    # TODO - ALSO CHECK OUT HOW FIXED CLASSES ARE PLAYING INTO DOUBLE PERIODS
