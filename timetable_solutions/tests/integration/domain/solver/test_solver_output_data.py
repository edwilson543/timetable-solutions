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
        spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
        )
        data = slvr.TimetableSolverInputs(
            school_id=school_access_key, solution_specification=spec
        )
        solver = slvr.TimetableSolver(input_data=data)
        solver.solve()

        # Execute test unit
        slvr.TimetableSolverOutcome(timetable_solver=solver)

        # Check the outcome
        expected_slots = models.TimetableSlot.objects.get_specific_timeslots(
            school_id=111111, slot_ids=[1, 2]
        )

        maths_a = models.Lesson.objects.get_individual_lesson(
            school_id=111111, lesson_id="YEAR_ONE_MATHS_A"
        )
        maths_b = models.Lesson.objects.get_individual_lesson(
            school_id=111111, lesson_id="YEAR_ONE_MATHS_B"
        )

        self.assertQuerysetEqual(
            expected_slots, maths_a.get_all_time_slots(), ordered=False
        )
        self.assertQuerysetEqual(
            expected_slots, maths_b.get_all_time_slots(), ordered=False
        )
