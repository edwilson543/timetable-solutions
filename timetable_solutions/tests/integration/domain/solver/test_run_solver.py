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
        Test that the solver can run end-to-end. Given only a school access key (for now), the solver should be able
        to load the required data, produce a timetable solution, and then save it back into the database.
        """
        # Set test parameters
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True,
                                          allow_triple_periods_and_above=True)

        # Execute
        error_messages = produce_timetable_solutions(school_access_key=222222, solution_specification=spec)

        # Check outcome - entirely new FixedClass instances should have been created in the database
        assert len(error_messages) == 0
        fixed_classes = models.FixedClass.objects.all()
        assert fixed_classes.count() == 2  # Within the test FIXTURE, there are zero
        for fc in fixed_classes:
            assert fc.time_slots.all().count() == 1
