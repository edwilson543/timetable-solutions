"""
Unit tests for the instantiation of solver variables
"""

# Standard library imports
from functools import lru_cache
from unittest import mock

# Django imports
from django import test

# Local application imports
from data import models
from domain import solver as slvr


class TestTimetableSolverVariables(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_without_solution.json",
    ]

    @staticmethod
    @lru_cache(maxsize=1)
    def get_variables_maker() -> slvr.TimetableSolverVariables:
        """
        Utility method used to return an instance of the class holding the timetable variables.
        Note that we patch the methods called at instantiation, to avoid silently testing that they work
        """
        solution_spec = slvr.SolutionSpecification(
            allow_split_classes_within_each_day=True,
            allow_triple_periods_and_above=True,
        )
        input_data = slvr.TimetableSolverInputs(
            school_id=123456, solution_specification=solution_spec
        )
        with mock.patch.object(
            slvr.TimetableSolverVariables, "_get_decision_variables", return_value=None
        ), mock.patch.object(
            slvr.TimetableSolverVariables,
            "_get_double_period_variables",
            return_value=None,
        ):
            variables_maker = slvr.TimetableSolverVariables(inputs=input_data)
        return variables_maker

    def test_get_decision_variables(self):
        """
        Test for the decision variable instantiation.
        """
        # Set parameters
        variables_maker = self.get_variables_maker()

        # Execute test unit
        variables = variables_maker._get_decision_variables()

        # Test the outcome - we expect one variable per lesson / timetable slot pair
        assert len(variables) == 12 * 35
        random_var_key = slvr.var_key(lesson_id="YEAR_ONE_FRENCH_A", slot_id=19)
        random_var = variables[random_var_key]
        assert random_var.lowBound == 0
        assert random_var.upBound == 1
        assert random_var.cat == "Integer"
        assert random_var.varValue is None

    def test_strip_decision_variables(self):
        """
        Test for the method removing irrelevant variables from the variables dict.
        """
        # Set parameters - we add two user defined slots at monday at 9AM, so that this variable gets stripped
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
        two_slots = models.TimetableSlot.objects.filter(slot_id__in=[1, 2])
        lesson.add_user_defined_time_slots(time_slots=two_slots)

        to_strip_variable_key_1 = slvr.var_key(lesson_id="YEAR_ONE_MATHS_A", slot_id=1)
        to_strip_variable_key_2 = slvr.var_key(lesson_id="YEAR_ONE_MATHS_A", slot_id=2)

        variables_maker = self.get_variables_maker()
        variables = variables_maker._get_decision_variables(strip=False)

        # Execute the test unit
        assert to_strip_variable_key_1 in variables.keys()
        assert to_strip_variable_key_2 in variables.keys()
        variables_maker._strip_decision_variables(variables=variables)

        # Test the outcome
        assert to_strip_variable_key_1 not in variables.keys()
        assert to_strip_variable_key_2 not in variables.keys()

    def test_get_double_period_variables(self):
        """
        Test of the dependent, double period variables instantiation.
        """
        # Set parameters
        variables_maker = self.get_variables_maker()

        # Execute test unit
        variables = variables_maker._get_double_period_variables()

        # Test the outcome - we expect one variable per consecutive period
        assert (
            len(variables)
            == 12 * 6 * 5  # 12 lessons, 6 consecutive periods / day, 5 days / week
        )
        random_var_key = slvr.doubles_var_key(
            lesson_id="YEAR_ONE_FRENCH_B", slot_1_id=7, slot_2_id=12
        )
        random_var = variables[random_var_key]
        assert random_var.lowBound == 0
        assert random_var.upBound == 1
        assert random_var.cat == "Integer"
        assert random_var.varValue is None
