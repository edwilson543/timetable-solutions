"""Unit tests for the instantiation of solver variables"""

# Third party imports
import pulp as lp

# Django imports
from django import test

# Local application imports
from domain.solver import linear_programming


class TestTimetableSolverVariables(test.TestCase):

    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json", "unsolved_classes.json"]

    def test_timetable_solver_get_variables(self):
        """
        Test of the variable instantiation process for some basic input data
        """
        # Set parameters
        input_data = linear_programming.TimetableSolverInputs(school_id=123456)

        # Execute test unit
        variables = linear_programming.TimetableSolverVariables(inputs=input_data).get_variables()

        # Test the outcome - we expect one variable per timetable slot / unsolved class pair
        assert len(variables) == 12 * 35

    def test_timetable_solver_strip_variables(self):
        """
        Test for the method removing irrelevant variables from the variables dict.
        """
        # Set parameters
        input_data = linear_programming.TimetableSolverInputs(school_id=123456)
        variable_maker = linear_programming.TimetableSolverVariables(inputs=input_data)
        variables = variable_maker.get_variables(strip=False)

        # We add and additional variable to the variables dictionary, to be stripped out, since we know lunch 1 happens
        # during slot 4
        additional_variable = {("LUNCH_1", 4): lp.LpVariable("Note that lp variable is irrelevant to test")}
        variables = variables | additional_variable

        # Execute the test unit  - note that LUNCH_1 is a know fixed class so we don't need a variable for it
        variable_maker._strip_variables(variables=variables)

        # Test the outcome
        assert ("LUNCH_4", 1) not in variables.keys()
