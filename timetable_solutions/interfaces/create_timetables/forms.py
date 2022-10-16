"""
Forms related to allowing users to specify their requirements for how the timetable solutions are found
"""

# Django imports
from django import forms

# Local application imports
from domain.solver import SolutionSpecification as _SolutionSpecification


class SolutionSpecification(forms.Form):
    """Form that the user must fill in each time they generate some solutions."""

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
        all_choices = [("NONE", "No preference")] + time_choices
        self.fields["optimal_free_period_time_of_day"].choices = all_choices

    def get_solution_specification_from_form_data(self) -> _SolutionSpecification:
        """
        Method to create a SolutionSpecification instance from the cleaned form data.
        """
        optimal_free_period = self.cleaned_data["optimal_free_period_time_of_day"]
        if optimal_free_period == "NONE":
            optimal_free_period = None

        spec = _SolutionSpecification(
            allow_split_classes_within_each_day=self.cleaned_data["allow_split_classes_within_each_day"],
            allow_triple_periods_and_above=self.cleaned_data["allow_triple_periods_and_above"],
            optimal_free_period_time_of_day=optimal_free_period
        )
        return spec
