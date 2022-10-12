"""
Forms related to allowing users to specify their requirements for how the timetable solutions are found
"""

# Django imports
from django import forms


class SolutionSpecification(forms.Form):
    """Form that the user must fill in each time they generate some solutions."""
    placeholder_1 = forms.BooleanField(label="PLACEHOLDER - Minimise year groups per teacher per day",
                                       widget=forms.CheckboxInput)
    placeholder_2 = forms.BooleanField(label="PLACEHOLDER - Maximise free period spacing", widget=forms.CheckboxInput)
    placeholder_3 = forms.BooleanField(label="PLACEHOLDER - Do not allow XYZ", widget=forms.CheckboxInput)
