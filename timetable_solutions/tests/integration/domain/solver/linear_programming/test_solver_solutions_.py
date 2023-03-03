"""Integration tests looking for specific timetable solutions from the TimetableSolver class."""


# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp

# Django imports
from django import test

# Local application imports
from domain import solver as slvr


class TestSolver(test.TestCase):
    """
    Test that the solver can produce a solution for the default fixtures.
    These fixtures are not contrived to produce a specific solution, so we do not test what the solution actually is.
    """

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_without_solution.json",
    ]

    def test_solver_finds_a_solution_for_default_fixtures_random_objective(self):
        """
        Test that the solver can find a problem for the full LP problem, EXCLUDING an objective, for the default
        fixture set.
        The objective is 'random' since we do not specify an 'optimal_free_period_time_of_day'
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
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome - i.e. that a solution has been found
        assert lp.LpStatus[solver.problem.status] == "Optimal"

    def test_solver_finds_a_solution_for_default_fixtures_with_non_random_objective(
        self,
    ):
        """
        Test that the solver can find a problem for the full LP problem, INCLUDING an objective, for the default
        fixture set.
        The objective is 'non-random' since we specify 'optimal_free_period_time_of_day' at a specific time
        """
        # Set test parameters
        school_access_key = 123456
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=False,
            allow_triple_periods_and_above=False,
            optimal_free_period_time_of_day=dt.time(hour=14),
            ideal_proportion_of_free_periods_at_this_time=0.75,
        )
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome - i.e. that a solution has been found
        assert lp.LpStatus[solver.problem.status] == "Optimal"


class TestSolverScenarioSolutionsConstraintDrivenRandomObjective(test.TestCase):
    """
    Tests where we are after a specific solution. See individual docstrings for scenario setups.
    'ConstraintDriven': The constraints are what determines the solution
    'RandomObjective': The objective is randomly generated, and as such should not affect the solution
    """

    fixtures = [
        "test_scenario_4.json",
        "test_scenario_8.json",
        "test_scenario_9.json",
        "test_scenario_10.json",
    ]

    # Note that test scenarios 7 and above do not use this solution spec
    solution_spec = slvr.SolutionSpecification(
        allow_split_classes_within_each_day=True, allow_triple_periods_and_above=True
    )

    # TESTS WHERE A BASIC CONSTRAINT IS LIMITING

    def test_solver_solution_test_scenario_4(self):
        """
        Test scenario targeted at the classroom one-class-at-a-time constraint.
        Two classes share a classroom, but neither pupils nor teachers. One must take place at a certain time, leaving
        only one option for the remaining class.
        """
        # Set test parameters
        school_access_key = 444444
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert (
            len(solver.variables.decision_variables) == 2
        )  # Lesson's 1 slot could go in either time slot
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=1)
            ].varValue
            == 0
        )  # Busy
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=2)
            ].varValue
            == 1
        )

    # TESTS WHERE A STRUCTURAL, OPTIONAL CONSTRAINT IS LIMITING
    def test_solver_solution_test_scenario_8(self):
        """
        Test scenario targeted at the no split classes constraints.
        We have the following setup:
        Timetable structure:
            Monday: Fixed-empty-empty;
            Tuesday: empty;
            Tuesday: 1 slot
        1 Lesson, requiring:
            2 total slots;
            0 double periods.
        By the no split classes constraint, the remaining class has to be taught on Tuesday. In particular, it cannot be
        taught at period 3 on Monday.
        """
        # Set test parameters
        school_access_key = 888888
        spec = slvr.SolutionSpecification(
            allow_triple_periods_and_above=True,  # True but irrelevant
            allow_split_classes_within_each_day=False,
        )
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert (
            len(solver.variables.decision_variables) == 3
        )  # 3 slots, 1 class, but one variable gets stripped

        # Slot_id 3 represents the individual slot on the Tuesday where we want the class to happen
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=2)
            ].varValue
            == 0
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=3)
            ].varValue
            == 0
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=4)
            ].varValue
            == 1
        )

    def test_solver_solution_test_scenario_9(self):
        """
        Test scenario targeted at the no two doubles in a day constraint (which is effectively also a no triples+
        constraint)
        We have the following setup:
        Timetable structure:
            Monday: empty-empty-empty-Fixed;
            Tuesday: empty-empty;
        1 Lesson, requiring:
            4 total slots;
            2 double period.
        By the no two doubles in a day constraint, we must have the following final structure:
            Monday: A - Solver-Solver-empty-User; OR B - Solver-empty-Solver-User - but we make the pupil /
            classroom / teacher incompatible with option B, so we always get option A
            Tuesday: Solver-Solver
        """
        # Set test parameters
        school_access_key = 999999
        spec = slvr.SolutionSpecification(
            allow_triple_periods_and_above=False,
            allow_split_classes_within_each_day=True,
        )
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert (
            len(solver.variables.decision_variables) == 5
        )  # 6 slots, 1 class, but one variable gets stripped
        assert (
            len(solver.variables.double_period_variables) == 4
        )  # 3 on the Monday, 1 on the Tuesday

        # See docstring for solution
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=1)
            ].varValue
            == 1
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=2)
            ].varValue
            == 1
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=3)
            ].varValue
            == 0
        )
        # slot_id=4 user defined so gets stripped
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=5)
            ].varValue
            == 1
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=6)
            ].varValue
            == 1
        )

    def test_solver_solution_test_scenario_10(self):
        """
        Test scenario targeted at using the no two doubles in a day constraint in combination with the no split classes
        constraint, as well as testing that the no split classes constraint isn't broken by a user-defined split
        We have the following setup:
        Timetable structure:
            Monday: empty-empty-empty-empty;
            Tuesday: empty-empty-empty-empty;
            Wednesday: empty
        1 Lesson, requiring:
            6 total slots;
            2 double period.
        Therefore, we expect a double at some point on Monday, a double at some point on Tuesday, and a single on
        Wednesday.
        """
        # Set test parameters
        school_access_key = 101010
        spec = slvr.SolutionSpecification(
            allow_triple_periods_and_above=False,
            allow_split_classes_within_each_day=False,
        )  # Note both False
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert (
            len(solver.variables.decision_variables) == 9
        )  # 9 slots, none get stripped
        assert (
            len(solver.variables.double_period_variables) == 6
        )  # 3 on the Monday, 3 on the Tuesday

        # See docstring for solution
        # Wednesday must happen
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=9)
            ].varValue
            == 1
        )

        # Must have exactly one double on Monday
        monday_1_2 = solver.variables.double_period_variables[
            slvr.doubles_var_key(lesson_id="ENGLISH", slot_1_id=1, slot_2_id=2)
        ].varValue
        monday_2_3 = solver.variables.double_period_variables[
            slvr.doubles_var_key(lesson_id="ENGLISH", slot_1_id=2, slot_2_id=3)
        ].varValue
        monday_3_4 = solver.variables.double_period_variables[
            slvr.doubles_var_key(lesson_id="ENGLISH", slot_1_id=3, slot_2_id=4)
        ].varValue
        assert sum([monday_1_2, monday_2_3, monday_3_4]) == 1

        # Must have exactly one double on Tuesday
        tuesday_1_2 = solver.variables.double_period_variables[
            slvr.doubles_var_key(lesson_id="ENGLISH", slot_1_id=5, slot_2_id=6)
        ].varValue
        tuesday_2_3 = solver.variables.double_period_variables[
            slvr.doubles_var_key(lesson_id="ENGLISH", slot_1_id=6, slot_2_id=7)
        ].varValue
        tuesday_3_4 = solver.variables.double_period_variables[
            slvr.doubles_var_key(lesson_id="ENGLISH", slot_1_id=7, slot_2_id=8)
        ].varValue
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
        Timetable structure:
            Monday: empty-empty-empty-empty;
        1 Lesson, requiring:
            1 slot;
        Optimal free period time:
            Slot 1;
        Since the optimal free period slot pushes slots away from it as much as possible, we expect the 1 slot to take
        place at slot 4.
        """
        # Set test parameters
        school_access_key = 111111
        optimal_free_period = dt.time(hour=9)
        spec = slvr.SolutionSpecification(
            allow_triple_periods_and_above=True,
            allow_split_classes_within_each_day=True,
            optimal_free_period_time_of_day=optimal_free_period,
        )
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 4
        assert len(solver.variables.double_period_variables) == 0

        # See docstring for solution
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=1)
            ].varValue
            == 0
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=2)
            ].varValue
            == 0
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=3)
            ].varValue
            == 0
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=4)
            ].varValue
            == 1
        )

    def test_solver_solution_test_scenario_with_objective_2_ideal_morning(self):
        """
        Test scenario targeted at using the optimal free period objective component, with the morning specified.
        We have the following setup:
        Timetable structure:
            Monday: MORNING: empty; AFTERNOON: empty;
        1 Lesson, requiring:
            1 slot;
        Optimal free period time:
            MORNING;
        Therefore we want the outcome to be that the lesson's one slot takes place in the AFTERNOON.
        """
        # Set test parameters
        school_access_key = 222222
        morning = slvr.SolutionSpecification.OptimalFreePeriodOptions.MORNING
        spec = slvr.SolutionSpecification(
            allow_triple_periods_and_above=True,
            allow_split_classes_within_each_day=True,
            optimal_free_period_time_of_day=morning,
        )
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 2
        assert len(solver.variables.double_period_variables) == 0

        # See docstring for solution
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=1)
            ].varValue
            == 0
        )  # Morn
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=2)
            ].varValue
            == 1
        )  # Aft

    def test_solver_solution_test_scenario_with_objective_2_ideal_afternoon(self):
        """
        Test scenario targeted at using the optimal free period objective component, with the afternoon specified.
        We have the following setup:
        Timetable structure:
            Monday: MORNING: empty; AFTERNOON: empty;
        1 Lesson, requiring:
            1 slot;
        Optimal free period time:
            AFTERNOON;
        Therefore we want the outcome to be that the lesson's one slot takes place in the MORNING.
        """
        # Set test parameters
        school_access_key = 222222
        afternoon = slvr.SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON
        spec = slvr.SolutionSpecification(
            allow_triple_periods_and_above=True,
            allow_split_classes_within_each_day=True,
            optimal_free_period_time_of_day=afternoon,
        )
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        assert len(solver.variables.decision_variables) == 2
        assert len(solver.variables.double_period_variables) == 0

        # See docstring for solution
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=1)
            ].varValue
            == 1
        )  # Morn
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=2)
            ].varValue
            == 0
        )  # Aft


class TestSolverScenarioSolutionsBreaks(test.TestCase):
    """
    Tests for specific solutions, where a Break instance drives the solution.
    """

    fixtures = ["test_scenario_break_1.json"]
    solution_spec = slvr.SolutionSpecification(
        allow_split_classes_within_each_day=True, allow_triple_periods_and_above=True
    )

    def test_scenario_break_1(self):
        """
        Test scenario targeted at the teacher one-place-at-a-time constraint,
        when a break clashes with a potential slot.
        A teacher teaches 1 lesson, which requires 2 slots.
        There are 3 slots, the middle one clashes with a break.
        None of the slots are consecutive so there is no need to worry about double periods.
        """
        # Set test parameters
        school_access_key = 111111
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        # We should have a decision variable for each of our 3 slots
        assert len(solver.variables.decision_variables) == 3

        # Slots 1 & 3 does not clash with the teacher's break, whereas slot 2 does.
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="MATHS", slot_id=1)
            ].varValue
            == 1
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="MATHS", slot_id=2)
            ].varValue
            == 0
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="MATHS", slot_id=3)
            ].varValue
            == 1
        )


class TestSolverScenarioSolutionsDifferentTimetablesForYearGroups(test.TestCase):
    """
    Tests for a specific solution, where the fact that different year groups have different timetables
    is what forces the test solution.
    """

    fixtures = ["diff_tts_scenario_1.json"]
    solution_spec = slvr.SolutionSpecification(
        allow_split_classes_within_each_day=True, allow_triple_periods_and_above=True
    )

    def test_diff_tts_scenario_1(self):
        """
        Test scenario targeted at teacher availability constraints.
        We have the following setup:
        Timetable structure:
            Year 1: Monday: 8:30-9:30; 10:30-11:30
            Year 2: Monday 9:00-10:00;
        2 Lessons:
            Year 1: Needs 1 slot, undefined
            Year 2: 1 slot fixed at 9:00-10:00
        1 teacher for both lessons
        Therefore, expected outcome is that the other lesson must be taught 10:30-11:30, otherwise
        the teacher has a clash.
        """
        # Set test parameters
        school_access_key = 111111
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        # The year 1 lesson could supposedly go in any of the 2 year 1 slots
        assert len(solver.variables.decision_variables) == 2

        # The teacher is busy 9:00-10:00, so other lesson must be taught at 10:30-11:30
        assert (
            solver.variables.decision_variables[
                slvr.var_key(
                    lesson_id="ENGLISH", slot_id=1
                )  # 8:30-9:30 - clash with when teacher already busy
            ].varValue
            == 0
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=2)  # 10:30-11:30 - no clash
            ].varValue
            == 1
        )

    def test_diff_tts_scenario_2(self):
        """
        Test scenario targeted at classroom availability constraints.
        We have the following setup:
        Timetable structure:
            Year 1: Monday: 8:30-9:30; 10:30-11:30
            Year 2: Monday 9:00-10:00;
        2 Lessons:
            Year 1: Needs 1 slot, undefined
            Year 2: 1 slot fixed at 9:00-10:00
        1 classroom for both lessons
        Therefore, expected outcome is that the other lesson must be taught 10:30-11:30, otherwise
        the teacher has a clash.
        """
        # Set test parameters
        school_access_key = 111111
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=self.solution_spec
        )
        solver = slvr.TimetableSolver(input_data=data)

        # Execute test unit
        solver.solve()

        # Check outcome
        assert lp.LpStatus[solver.problem.status] == "Optimal"
        # The year 1 lesson could supposedly go in any of the 2 year 1 slots
        assert len(solver.variables.decision_variables) == 2

        # The teacher is busy 9:00-10:00, so other lesson must be taught at 10:30-11:30
        assert (
            solver.variables.decision_variables[
                slvr.var_key(
                    lesson_id="ENGLISH", slot_id=1
                )  # 8:30-9:30 - clash with when teacher already busy
            ].varValue
            == 0
        )
        assert (
            solver.variables.decision_variables[
                slvr.var_key(lesson_id="ENGLISH", slot_id=2)  # 10:30-11:30 - no clash
            ].varValue
            == 1
        )
