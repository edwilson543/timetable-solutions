"""Unit tests for the instantiation of solver variables"""

# Third party imports
import pulp as lp
import pytest

# Local application imports
from domain.solver import linear_programming


class TestTimetableSolverVariables:

    @pytest.fixture(scope="class")
    def solver_variables(self, unsolved_class_data, fixed_class_data,
                         timetable_slot_data) -> linear_programming.TimetableSolverVariables:
        """
        Fixture for the class used to make pulp variables, bound to some simulated input data
        """
        inputs = linear_programming.TimetableSolverInputs(data_location=None)
        inputs.unsolved_class_data = unsolved_class_data
        inputs.fixed_class_data = fixed_class_data
        inputs.timetable_slot_data = timetable_slot_data
        variables_maker = linear_programming.TimetableSolverVariables(inputs=inputs)
        return variables_maker

    def test_timetable_solver_get_variables(self, solver_variables):
        """
        Test of the variable instantiation process for some basic input data
        """
        # Execute test unit
        variables = solver_variables.get_variables()

        # Test the outcome - fixed classes at A-1, A-2 and B-3, B-4, so these get stripped out
        assert set(variables.keys()) == {("A", 3), ("A", 4), ("B", 1), ("B", 2)}
        for var in variables.values():
            assert isinstance(var, lp.LpVariable)

    def test_timetable_solver_strip_variables(self, solver_variables):
        """
        Test for the method removing irrelevant variables from the variables dict.
        """
        # Set test parameters
        variable_keys = {("A", 1),  # Should get stripped, since class "A" is fixed for timetable slot 1 in the inputs
                     ("A", 3), ("A", 4), ("B", 1), ("B", 2)}
        variables = {key: lp.LpVariable("Note that lp variable is irrelevant to test") for key in variable_keys}

        # Execute the test unit
        solver_variables._strip_variables(variables=variables)

        # Test the outcome
        assert set(variables.keys()) == {("A", 3), ("A", 4), ("B", 1), ("B", 2)}
