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

    # Choices for fields
    OPTIMAL_FREE_PERIOD_CHOICES = [(_SolutionSpecification.OptimalFreePeriodOptions.NONE, "No preference"),
                                   (_SolutionSpecification.OptimalFreePeriodOptions.MORNING, "Morning"),
                                   (_SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON, "Afternoon")]
    IDEAL_PROPORTION_CHOICES = [(value / 100, f"{value}%") for value in range(100, 0, -10)]

    # Form fields
    allow_split_classes_within_each_day = forms.BooleanField(
        label="Allow each class to be taught more than once in a day", label_suffix="", widget=forms.CheckboxInput,
        required=False)
    allow_triple_periods_and_above = forms.BooleanField(
        label="Allow triple periods or longer", label_suffix="", widget=forms.CheckboxInput, required=False)
    optimal_free_period_time_of_day = forms.ChoiceField(
        label="Best time of day for free periods", label_suffix="", choices=OPTIMAL_FREE_PERIOD_CHOICES, required=True)
    ideal_proportion_of_free_periods_at_this_time = forms.TypedChoiceField(
        label="Ideal proportion of free periods at this time", label_suffix="", choices=IDEAL_PROPORTION_CHOICES,
        required=True, coerce=float)

    def __init__(self, *args, **kwargs):
        """
        Customise the init method to provide dynamic choices as relevant
        :kwargs available_time_slots - the times of day which the user who is being shown this form has timetable slots
        starting at (inferred from their uploaded data)
        """
        available_time_slots = kwargs.pop("available_time_slots")
        super().__init__(*args, **kwargs)

        time_choices = [(slot, slot.strftime("%H:%M")) for slot in available_time_slots]
        self.fields["optimal_free_period_time_of_day"].choices += time_choices

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
            # The optimal_free_period is one of the string options from _SolutionSpecification
            pass

        self.cleaned_data["optimal_free_period_time_of_day"] = optimal_free_period
        return self.cleaned_data

    def get_solution_specification_from_form_data(self) -> _SolutionSpecification:
        """
        Method to create a SolutionSpecification instance from the cleaned form data.
        """
        spec = _SolutionSpecification(
            allow_split_classes_within_each_day=self.cleaned_data["allow_split_classes_within_each_day"],
            allow_triple_periods_and_above=self.cleaned_data["allow_triple_periods_and_above"],
            optimal_free_period_time_of_day=self.cleaned_data["optimal_free_period_time_of_day"],
            ideal_proportion_of_free_periods_at_this_time=self.cleaned_data[
                "ideal_proportion_of_free_periods_at_this_time"]
        )
        return spec
