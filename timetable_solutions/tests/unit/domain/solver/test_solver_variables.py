"""Unit tests for the instantiation of solver variables"""

# Third party imports
import pulp as lp

# Django imports
from django import test

# Local application imports
from domain import solver as slvr


class TestTimetableSolverVariables(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json", "unsolved_classes.json"]

    def test_get_decision_variables(self):
        """
        Test for the decision variable instantiation
        """
        # Set parameters
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True)
        input_data = slvr.TimetableSolverInputs(school_id=123456, solution_specification=spec)

        # Execute test unit
        variables_maker = slvr.TimetableSolverVariables(inputs=input_data, set_variables=False)
        variables = variables_maker._get_decision_variables()

        # Test the outcome - we expect one variable per timetable slot / unsolved class pair
        assert len(variables) == 12 * 35
        random_var_key = slvr.var_key(class_id="YEAR_ONE_FRENCH_A", slot_id=19)
        random_var = variables[random_var_key]
        assert random_var.lowBound == 0
        assert random_var.upBound == 1
        assert random_var.cat == "Integer"
        assert random_var.varValue is None

    def test_strip_decision_variables(self):
        """
        Test for the method removing irrelevant variables from the variables dict.
        """
        # Set parameters
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True)
        input_data = slvr.TimetableSolverInputs(school_id=123456, solution_specification=spec)
        variable_maker = slvr.TimetableSolverVariables(inputs=input_data, set_variables=False)
        variables = variable_maker._get_decision_variables(strip=False)

        # We add an additional variable to the variables dictionary, to be stripped out
        variable_key = slvr.var_key(class_id="LUNCH_1", slot_id=21)
        additional_variable = {variable_key: lp.LpVariable("Note that l_p variable is irrelevant to test")}
        variables = variables | additional_variable

        # Execute the test unit  - note that LUNCH_1 is a know fixed class so we don't need a variable for it
        variable_maker._strip_decision_variables(variables=variables)

        # Test the outcome
        assert variable_key not in variables.keys()

    def test_get_double_period_variables(self):
        """
        Test for the decision variable instantiation
        """
        # Set parameters
        spec = slvr.SolutionSpecification(allow_split_classes_within_each_day=True)
        input_data = slvr.TimetableSolverInputs(school_id=123456, solution_specification=spec)

        # Execute test unit
        variables_maker = slvr.TimetableSolverVariables(inputs=input_data, set_variables=False)
        variables = variables_maker._get_double_period_variables()

        # Test the outcome - we expect one variable per consecutive period
        assert len(variables) == 12 * 6 * 5  # 12 unsolved classes, 6 consecutive periods / day, 5 days / week
        random_var_key = slvr.doubles_var_key(class_id="YEAR_ONE_FRENCH_B", slot_1_id=7, slot_2_id=12)
        random_var = variables[random_var_key]
        assert random_var.lowBound == 0
        assert random_var.upBound == 1
        assert random_var.cat == "Integer"
        assert random_var.varValue is None
