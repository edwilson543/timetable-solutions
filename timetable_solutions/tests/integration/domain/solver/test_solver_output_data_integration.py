"""
Integration test for the TimetableSolverOutcome
"""

# Django imports
from django import test

# Local application imports
from data import models
from domain import solver as slvr


class TestTimetableSolverOutcome(test.TestCase):

    fixtures = ["test_scenario_1.json"]

    def test_timetable_solver_integration_test_scenario_1(self):
        """
        Test for extracting a specific solution from the timetable solver. Instantiating te TimetableSolverOutcome
        instance should initiate and complete all processing, so we check that this is indeed the case.
        """
        # Set test parameters
        school_access_key = 111111
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True)
        data = slvr.TimetableSolverInputs(school_id=school_access_key, solution_specification=spec)
        solver = slvr.TimetableSolver(input_data=data)
        solver.solve()

        # Execute test unit
        outcome = slvr.TimetableSolverOutcome(timetable_solver=solver)

        # Check the outcome
        expected_slots = models.TimetableSlot.objects.get_specific_timeslots(school_id=111111, slot_ids=[1, 2])
        fc_maths_a = models.FixedClass.objects.get_individual_fixed_class(
            school_id=111111, class_id="YEAR_ONE_MATHS_A")
        fc_maths_b = models.FixedClass.objects.get_individual_fixed_class(
            school_id=111111, class_id="YEAR_ONE_MATHS_B")
        self.assertQuerysetEqual(expected_slots, fc_maths_a.time_slots.all(), ordered=False)
        self.assertQuerysetEqual(expected_slots, fc_maths_b.time_slots.all(), ordered=False)
