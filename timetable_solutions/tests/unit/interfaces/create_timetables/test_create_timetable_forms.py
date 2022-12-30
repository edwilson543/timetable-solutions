"""
Module containing unit tests for the SolutionSpecification form in the create_timetables app.
"""

# Standard library imports
import datetime as dt

# Local application imports
from interfaces.create_timetables import forms


def test_solution_specification_form_instantiation():
    """
    Test that passing available slots to the SolutionSpecification's __init__ adds to the choices on the relevant field
    """
    # Set test parameters
    available_time_slots = [dt.time(hour=9), dt.time(hour=10)]
    slots_as_choices = [(dt.time(hour=9), "09:00"), (dt.time(hour=10), "10:00")]
    expected_choices = (
        forms.SolutionSpecification.OPTIMAL_FREE_PERIOD_CHOICES + slots_as_choices
    )

    # Execute test unit
    form = forms.SolutionSpecification(available_time_slots=available_time_slots)

    # Check outcome
    assert (
        form.fields.get("optimal_free_period_time_of_day").choices == expected_choices
    )
