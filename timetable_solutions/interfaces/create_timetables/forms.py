"""
Forms related to allowing users to specify their requirements for how the timetable solutions are found
"""

# Standard library imports
import datetime as dt
from typing import Dict

# Django imports
from django import forms

# Local application imports
from domain.solver import SolutionSpecification as _SolutionSpecification


class SolutionSpecification(forms.Form):
    """Form that the user must fill in each time they generate some solutions."""

    _SERIALIZED_NONE = "NONE"  # String we use to represent the python None object in the form

    allow_split_classes_within_each_day = forms.BooleanField(
        label="Allow each class to be taught more than once in a day", label_suffix="", widget=forms.CheckboxInput,
        required=False)
    allow_triple_periods_and_above = forms.BooleanField(
        label="Allow triple periods or longer", label_suffix="", widget=forms.CheckboxInput, required=False)
    optimal_free_period_time_of_day = forms.ChoiceField(
        label="Best time of day for free periods", label_suffix="", choices=(), required=True)

    def __init__(self, *args, **kwargs):
        """
        Customise the init method to provide dynamic choices as relevant
        :param available_time_slots - the times of day which the user who is being shown this form has already specified
        that their timetable slots start at.
        """
        available_time_slots = kwargs.pop("available_time_slots")
        super().__init__(*args, **kwargs)

        time_choices = [(slot, slot.strftime("%H:%M")) for slot in available_time_slots]
        all_choices = [(self._SERIALIZED_NONE, "No preference")] + time_choices
        self.fields["optimal_free_period_time_of_day"].choices = all_choices

    def clean(self) -> Dict:
        """
        Method adding some additional cleaning to the submitted form. This is needed since we have mixed types in our
        free period choice field, and so in particular need to produce a dt.time instance from the time strings.
        :return: the dictionary of cleaned form data, with the field names as keys
        """
        cleaned_data = super().clean()
        optimal_free_period = self.cleaned_data["optimal_free_period_time_of_day"]
        try:
            optimal_free_period = dt.datetime.strptime(optimal_free_period, "%H:%M:%S").time()

        except ValueError:
            optimal_free_period = None

        self.cleaned_data["optimal_free_period_time_of_day"] = optimal_free_period
        return self.cleaned_data

    def get_solution_specification_from_form_data(self) -> _SolutionSpecification:
        """
        Method to create a SolutionSpecification instance from the cleaned form data.
        """
        spec = _SolutionSpecification(
            allow_split_classes_within_each_day=self.cleaned_data["allow_split_classes_within_each_day"],
            allow_triple_periods_and_above=self.cleaned_data["allow_triple_periods_and_above"],
            optimal_free_period_time_of_day=self.cleaned_data["optimal_free_period_time_of_day"]
        )
        return spec




