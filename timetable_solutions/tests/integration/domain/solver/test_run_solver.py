"""
Integration test for running the solver end-to-end
"""

# Django imports
from django import test

# Local application imports
from data import models
from domain.solver.run_solver import produce_timetable_solutions
from domain import solver as slvr


class TestRunSolver(test.TestCase):
    fixtures = ["test_scenario_2.json"]

    def test_run_solver_test_scenario_2(self):
        """
        Test that the solver can run end-to-end. The solver should be able to load the required data,
        produce a timetable solution, and then save it in the database.
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True)

        # Execute
        error_messages = produce_timetable_solutions(school_access_key=222222, solution_specification=spec)

        # Check outcome - note we don't test for a specific solution
        assert len(error_messages) == 0
        lessons = models.Lesson.objects.all()

        for lesson in lessons:
            assert lesson.solver_defined_time_slots.count() == 1
