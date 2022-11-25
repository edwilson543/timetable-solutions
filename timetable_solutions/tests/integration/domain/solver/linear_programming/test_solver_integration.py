"""
Integration tests for the TimetableSolver class.

The following three test classes are present in this module:
    1) TestSolver - simply checks the solver can find a solution using the default fixtures
    2) TestSolverScenarioSolutionsNoObjective - checks for specific solutions in some manufactured scenarios, all of
      which DO NOT include an objective function
    3) TestSolverScenarioSolutionsWithObjective - checks for specific solutions in some manufactured scenarios, all of
      which include an objective function
"""

# Standard library imports
import datetime as dt

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
                "lessons_without_solution.json"]

    def test_solver_finds_a_solution_for_default_fixtures_random_objective(self):
        """
        Test that the solver can find a problem for the full LP problem, EXCLUDING an objective, for the default
        fixture set.
        The objective is 'random' since we do not specify an 'optimal_free_period_time_of_day'
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

    def test_solver_finds_a_solution_for_default_fixtures_with_non_random_objective(self):
        """
        Test that the solver can find a problem for the full LP problem, INCLUDING an objective, for the default
        fixture set.
        The objective is 'non-random' since we specify 'optimal_free_period_time_of_day' at a specific time
        """
        # Set test parameters
        school_access_key = 123456
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=False,
                                          allow_triple_periods_and_above=False,
                                          optimal_free_period_time_of_day=dt.time(hour=14),
                                          ideal_proportion_of_free_periods_at_this_time=0.75)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome - i.e. that a solution has been found
        assert lp.LpStatus[solver.problem.status] == "Optimal"


class TestSolverScenarioSolutionsConstraintDrivenRandomObjective(test.TestCase):
    """
    Tests where we are after a specific solution. See individual docstrings for scenario setups.
    'ConstraintDriven': The constraints are what determines the solution
    'RandomObjective': The objective is randomly generated, and as such should not drive the solution
    """

    fixtures = ["test_scenario_1.json", "test_scenario_2.json", "test_scenario_3.json", "test_scenario_4.json",
                "test_scenario_5.json", "test_scenario_6.json", "test_scenario_7", "test_scenario_8.json",
                "test_scenario_9.json", "test_scenario_10.json"]

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
        We have the following setup:
        FixedClass / Timetable structure:
            Monday: empty-empty;
            Tuesday: empty;
        1 Unsolved Class, requiring:
            2 total slots;
            1 double period.
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

        We have the following setup:
        FixedClass / Timetable structure:
            Monday: empty-empty;
            Tuesday: empty-Fixed;
        1 Unsolved Class, requiring:
            2 total slots;
            1 double period.
        Therefore the solution is to attach a second slot to the already defined slot, making the double.
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

    def test_solver_solution_test_scenario_7(self):
        """
        Test scenario targeted at the component of the double period dependency constraint which states that adding an
        unsolved class next to a fixed class results in a double period.
        We have the following setup:
        FixedClass / Timetable structure:
            Monday: Fixed-Fixed-empty-empty-Fixed;
            Tuesday: empty;
            Tuesday: 1 slot
        1 Unsolved Class, requiring:
            4 total slots;
            1 double period.
        Since there is already a double on Monday, and adding a single in either of the available slots would create
        another double, the class must go on the Tuesday.
        """
        # Set test parameters
        school_access_key = 777777
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=self.solution_spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 3  # 6 slots, 1 class, but three variable gets stripped
        assert len(solver.variables.double_period_variables) == 4  # 4 possibles on the Monday, 0 on Tuesday

        # See docstring for solution
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=3)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=4)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=6)].varValue == 1

    # TESTS WHERE A STRUCTURAL, OPTIONAL CONSTRAINT IS LIMITING
    def test_solver_solution_test_scenario_8(self):
        """
        Test scenario targeted at the no split classes constraints.
        We have the following setup:
        FixedClass / Timetable structure:
            Monday: Fixed-empty-empty;
            Tuesday: empty;
            Tuesday: 1 slot
        1 Unsolved Class, requiring:
            2 total slots;
            0 double periods.
        By the no split classes constraint, the remaining class has to be taught on Tuesday. In particular, it cannot be
        taught at period 3 on Monday.
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
        assert len(solver.variables.decision_variables) == 3  # 3 slots, 1 class, but one variable gets stripped

        # Slot_id 3 represents the individual slot on the Tuesday where we want the class to happen
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=3)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=4)].varValue == 1

    def test_solver_solution_test_scenario_9(self):
        """
        Test scenario targeted at the no two doubles in a day constraint (which is effectively also a no triples+
        constraint)
        We have the following setup:
        Fixed Class / Timetable structure:
            Monday: empty-empty-empty-Fixed;
            Tuesday: empty-empty;
        1 Unsolved Class, requiring:
            4 total slots;
            2 double period.
        By the no two doubles in a day constraint, we must have the following final structure:
            Monday: A - Unsolved-Unsolved-empty-Fixed; OR B - Unsolved-empty-Unsolved-Fixed - but we make the pupil /
            classroom / teacher incompatible with option B, so we always get option A
            Tuesday: Unsolved-Unsolved
        """
        # Set test parameters
        school_access_key = 999999
        spec = slvr.SolutionSpecification(allow_triple_periods_and_above=False,
                                          allow_split_classes_within_each_day=True)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 5  # 6 slots, 1 class, but one variable gets stripped
        assert len(solver.variables.double_period_variables) == 4  # 3 on the Monday, 1 on the Tuesday

        # See docstring for solution
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue == 1
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 1
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=3)].varValue == 0
        # 4 Fixed so was stripped
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=5)].varValue == 1
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=6)].varValue == 1

    def test_solver_solution_test_scenario_10(self):
        """
        Test scenario targeted at using the no two doubles in a day constraint in combination with the no split classes
        constraint, as well as testing that the no split classes constraint isn't broken by a user-defined split
        We have the following setup:
        Fixed Class / Timetable structure:
            Monday: empty-empty-empty-empty;
            Tuesday: empty-empty-empty-empty;
            Wednesday: empty
        1 Unsolved Class, requiring:
            6 total slots;
            2 double period.
        Therefore we expect a double at some point on Monday, a double at some point on Tuesday, and a single on
        Wednesday.
        """
        # Set test parameters
        school_access_key = 101010
        spec = slvr.SolutionSpecification(allow_triple_periods_and_above=False,
                                          allow_split_classes_within_each_day=False)  # Note both False
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 9  # 9 slots, none get stripped
        assert len(solver.variables.double_period_variables) == 6  # 3 on the Monday, 3 on the Tuesday

        # See docstring for solution
        # Wednesday must happen
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=9)].varValue == 1

        # Must have exactly one double on Monday
        monday_1_2 = solver.variables.double_period_variables[slvr.doubles_var_key(
            class_id="ENGLISH", slot_1_id=1, slot_2_id=2)].varValue
        monday_2_3 = solver.variables.double_period_variables[slvr.doubles_var_key(
            class_id="ENGLISH", slot_1_id=2, slot_2_id=3)].varValue
        monday_3_4 = solver.variables.double_period_variables[slvr.doubles_var_key(
            class_id="ENGLISH", slot_1_id=3, slot_2_id=4)].varValue
        assert sum([monday_1_2, monday_2_3, monday_3_4]) == 1

        # Must have exactly one double on Tuesday
        tuesday_1_2 = solver.variables.double_period_variables[slvr.doubles_var_key(
            class_id="ENGLISH", slot_1_id=5, slot_2_id=6)].varValue
        tuesday_2_3 = solver.variables.double_period_variables[slvr.doubles_var_key(
            class_id="ENGLISH", slot_1_id=6, slot_2_id=7)].varValue
        tuesday_3_4 = solver.variables.double_period_variables[slvr.doubles_var_key(
            class_id="ENGLISH", slot_1_id=7, slot_2_id=8)].varValue
        assert sum([tuesday_1_2, tuesday_2_3, tuesday_3_4]) == 1


class TestSolverScenarioSolutionsObjectiveDriven(test.TestCase):
    """
    Tests where we are after a specific solution. See individual docstrings for scenario setups.
    'ObjectiveDrive' - the scenario is setup such that the optimal solution is entirely dictated by the objective
    function.
    """

    fixtures = ["test_scenario_objective_1.json", "test_scenario_objective_2.json"]

    def test_solver_solution_test_scenario_with_objective_1(self):
        """
        Test scenario targeted at using the optimal free period objective component, with a specific time of day.
        We have the following setup:
        Fixed Class / Timetable structure:
            Monday: empty-empty-empty-empty;
        1 Unsolved Class, requiring:
            1 slot;
        Optimal free period time:
            Slot 1;
        Since the optimal free period slot pushes slots away from it as much as possible, we expect the 1 slot to take
        place at slot 4.
        """
        # Set test parameters
        school_access_key = 111111
        optimal_free_period = dt.time(hour=9)
        spec = slvr.SolutionSpecification(allow_triple_periods_and_above=True,
                                          allow_split_classes_within_each_day=True,
                                          optimal_free_period_time_of_day=optimal_free_period)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 4
        assert len(solver.variables.double_period_variables) == 0

        # See docstring for solution
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=3)].varValue == 0
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=4)].varValue == 1

    def test_solver_solution_test_scenario_with_objective_2_ideal_morning(self):
        """
        Test scenario targeted at using the optimal free period objective component, with the morning specified.
        We have the following setup:
        Fixed Class / Timetable structure:
            Monday: MORNING: empty; AFTERNOON: empty;
        1 Unsolved Class, requiring:
            1 slot;
        Optimal free period time:
            MORNING;
        Therefore we want the outcome to be that that the unsolved class' one slot takes place in the AFTERNOON.
        """
        # Set test parameters
        school_access_key = 222222
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        spec = slvr.SolutionSpecification(allow_triple_periods_and_above=True,
                                          allow_split_classes_within_each_day=True,
                                          optimal_free_period_time_of_day=morning)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 2
        assert len(solver.variables.double_period_variables) == 0

        # See docstring for solution
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue == 0  # Morn
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 1  # Aft

    def test_solver_solution_test_scenario_with_objective_2_ideal_afternoon(self):
        """
        Test scenario targeted at using the optimal free period objective component, with the afternoon specified.
        We have the following setup:
        Fixed Class / Timetable structure:
            Monday: MORNING: empty; AFTERNOON: empty;
        1 Unsolved Class, requiring:
            1 slot;
        Optimal free period time:
            AFTERNOON;
        Therefore we want the outcome to be that that the unsolved class' one slot takes place in the MORNING.
        """
        # Set test parameters
        school_access_key = 222222
        afternoon = slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON
        spec = slvr.SolutionSpecification(allow_triple_periods_and_above=True,
                                          allow_split_classes_within_each_day=True,
                                          optimal_free_period_time_of_day=afternoon)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 2
        assert len(solver.variables.double_period_variables) == 0

        # See docstring for solution
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=1)].varValue == 1  # Morn
        assert solver.variables.decision_variables[slvr.var_key(class_id="ENGLISH", slot_id=2)].varValue == 0  # Aft
