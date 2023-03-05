"""Integration tests looking for specific timetable solutions from the TimetableSolver class."""

# Third party imports
import pulp as lp

# Django imports
from django import test

# Local application imports
from domain import solver as slvr


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
