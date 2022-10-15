"""
Forms related to allowing users to specify their requirements for how the timetable solutions are found
"""

# Django imports
from django import forms


class SolutionSpecification(forms.Form):
    """Form that the user must fill in each time they generate some solutions."""
    allow_split_classes_within_each_day = forms.BooleanField(
        label="Allow each class to be taught more than once in a day", label_suffix="", widget=forms.CheckboxInput,
        required=False)
    allow_triple_periods_and_above = forms.BooleanField(
        label="Allow triple periods or longer", label_suffix="", widget=forms.CheckboxInput, required=False)
