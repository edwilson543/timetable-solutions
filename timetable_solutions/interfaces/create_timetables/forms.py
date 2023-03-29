"""
Forms relating to generating timetable solutions.
"""

# Standard library imports
import datetime as dt
from typing import Any

# Django imports
from django import forms

# Local application imports
from domain.solver import SolutionSpecification as _SolutionSpecification

TIME_FORMAT = "%H:%M"


class SolutionSpecification(forms.Form):
    """Form that the user must fill in each time they generate some solutions."""

    # Choices for fields
    OPTIMAL_FREE_PERIOD_CHOICES = [
        (_SolutionSpecification.OptimalFreePeriodOptions.NONE, "No preference"),
        (_SolutionSpecification.OptimalFreePeriodOptions.MORNING, "Morning"),
        (_SolutionSpecification.OptimalFreePeriodOptions.AFTERNOON, "Afternoon"),
    ]
    IDEAL_PROPORTION_CHOICES = [
        (value / 100, f"{value}%") for value in range(100, 0, -10)
    ]

    # Form fields
    allow_split_lessons_within_each_day = forms.BooleanField(
        label="Classes can be taught at separate times in a day",
        label_suffix="",
        widget=forms.CheckboxInput,
        required=False,
    )
    allow_triple_periods_and_above = forms.BooleanField(
        label="Allow triple periods or longer",
        label_suffix="",
        widget=forms.CheckboxInput,
        required=False,
    )
    optimal_free_period_time_of_day = forms.ChoiceField(
        label="Best time of day for free periods",
        label_suffix="",
        choices=OPTIMAL_FREE_PERIOD_CHOICES,
        required=True,
    )
    ideal_proportion_of_free_periods_at_this_time = forms.TypedChoiceField(
        label="Ideal proportion of free periods at this time",
        label_suffix="",
        choices=IDEAL_PROPORTION_CHOICES,
        required=False,
    )

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Customise the init method to provide dynamic choices as relevant
        :kwargs available_time_slots - the times of day which the user who is being shown this form has timetable slots
        starting at (inferred from their uploaded data)
        """
        available_time_slots = kwargs.pop("available_time_slots")
        super().__init__(*args, **kwargs)

        time_choices = [
            (slot.strftime(TIME_FORMAT), slot.strftime(TIME_FORMAT))
            for slot in available_time_slots
        ]
        self.fields["optimal_free_period_time_of_day"].choices += time_choices

    def clean_optimal_free_period_time_of_day(self) -> str | dt.time | None:
        """
        Try converting the optimal free period time into a dt.time instance.
        """
        optimal_free_period = self.cleaned_data.get("optimal_free_period_time_of_day")
        try:
            optimal_free_period = dt.datetime.strptime(
                optimal_free_period, TIME_FORMAT
            ).time()
        except ValueError:
            # The optimal_free_period is one of the string options from _SolutionSpecification
            pass
        return optimal_free_period

    def clean_ideal_proportion_of_free_periods_at_this_time(self) -> float:
        """
        Try converting the ideal proportion into a float, if one was given.
        """
        if not (
            ideal_proportion := self.cleaned_data.get(
                "ideal_proportion_of_free_periods_at_this_time"
            )
        ):
            ideal_proportion = 1.0
        return ideal_proportion

    def get_solution_specification_from_form_data(self) -> _SolutionSpecification:
        """
        Method to create a SolutionSpecification instance from the cleaned form data.
        """
        spec = _SolutionSpecification(
            allow_split_lessons_within_each_day=self.cleaned_data.get(
                "allow_split_lessons_within_each_day", False
            ),
            allow_triple_periods_and_above=self.cleaned_data.get(
                "allow_triple_periods_and_above", False
            ),
            optimal_free_period_time_of_day=self.cleaned_data[
                "optimal_free_period_time_of_day"
            ],
            ideal_proportion_of_free_periods_at_this_time=self.cleaned_data[
                "ideal_proportion_of_free_periods_at_this_time"
            ],
        )
        return spec
