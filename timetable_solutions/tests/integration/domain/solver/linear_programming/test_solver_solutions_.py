"""Integration tests looking for specific timetable solutions from the TimetableSolver class."""


# Standard library imports
import datetime as dt

# Third party imports
import pulp as lp

# Django imports
from django import test

# Local application imports
from domain import solver as slvr


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
            allow_split_lessons_within_each_day=True,
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
            allow_split_lessons_within_each_day=True,
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
            allow_split_lessons_within_each_day=True,
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
        allow_split_lessons_within_each_day=True, allow_triple_periods_and_above=True
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
        allow_split_lessons_within_each_day=True, allow_triple_periods_and_above=True
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
