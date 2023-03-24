"""
Forms relating to the Break model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from data import constants, models
from domain.solver.filters import clashes as clash_filters
from interfaces.data_management.forms import base_forms


class BreakSearch(django_forms.Form):
    """
    Search form for the Break model.
    """

    search_term = django_forms.CharField(
        required=False, label="Search for a break by name or id."
    )

    day_of_week = django_forms.TypedChoiceField(
        required=False,
        choices=constants.Day.choices,
        label="Day of week",
        empty_value=None,
        initial=None,
        coerce=int,
    )

    year_group = django_forms.ModelChoiceField(
        required=False,
        label="Year group",
        empty_label="",
        queryset=models.YearGroupQuerySet().none(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Get and set the year group choices.
        """
        self.school_id = kwargs.pop("school_id")
        year_groups = models.YearGroup.objects.get_all_instances_for_school(
            school_id=self.school_id
        ).order_by("year_group_name")
        self.base_fields["year_group"].queryset = year_groups

        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        """
        Ensure some search criteria was given.
        """
        slot_id = self.cleaned_data.get("slot_id", None)
        day = self.cleaned_data.get("day_of_week", None)
        year_group = self.cleaned_data["year_group"]
        if not (slot_id or day or year_group):
            raise django_forms.ValidationError("Please enter a search term!")

        return self.cleaned_data


class BreakUpdateYearGroups(django_forms.Form):
    """
    Form for updating the year groups relevant to a particular break.
    """

    relevant_year_groups = django_forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.TimetableSlotQuerySet().none(),
        label="Select the year groups that this break slot is relevant to",
    )

    def __init__(self, *args: object, **kwargs: Any) -> None:
        self.school_id = kwargs.pop("school_id")
        break_ = kwargs.pop("break_")
        self.break_ = models.Break.objects.get(
            school_id=self.school_id, break_id=break_.break_id
        )

        # Set all this school's year groups as the options
        self.base_fields[
            "relevant_year_groups"
        ].queryset = models.YearGroup.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        # ...but only the year groups currently assigned to this slot as the initial values
        self.base_fields[
            "relevant_year_groups"
        ].initial = break_.relevant_year_groups.all().values_list("pk", flat=True)

        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        """
        Check the slot can be made relevant to the selected year groups
        """
        self._raise_if_no_year_group_selected()
        self._raise_if_clashes_produced_for_a_year_group()
        return self.cleaned_data

    def _raise_if_no_year_group_selected(self) -> None:
        if not self.cleaned_data["relevant_year_groups"]:
            raise django_forms.ValidationError(
                "You must select at least one year group!"
            )

    def _raise_if_clashes_produced_for_a_year_group(self) -> None:
        time_of_week = clash_filters.TimeOfWeek.from_break(self.break_)
        relevant_year_groups = self.cleaned_data["relevant_year_groups"]

        # Check for clashes with breaks
        check_against_breaks = models.Break.objects.filter(
            relevant_year_groups__in=relevant_year_groups
        ).exclude(break_id=self.break_.break_id)
        break_clash_str = _get_break_clash_str(
            time_of_week=time_of_week, check_against_breaks=check_against_breaks
        )

        # Check for clashes with slots
        check_against_slots = models.TimetableSlot.objects.filter(
            relevant_year_groups__in=relevant_year_groups
        )
        slot_clash_str = _get_slot_clash_str(
            time_of_week=time_of_week, check_against_slots=check_against_slots
        )

        if break_clash_str and slot_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be assigned to these year groups, since at least one year group has a "
                f"break at {break_clash_str} and slot at {slot_clash_str} clashing with this time."
            )
        elif break_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be assigned to these year groups, since at least one year group has a "
                f"break at {break_clash_str} clashing with this time."
            )
        elif slot_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be assigned to these year groups, since at least one year group has a "
                f"slot at {slot_clash_str} clashing with this time."
            )


def _get_break_clash_str(
    time_of_week: clash_filters.TimeOfWeek, check_against_breaks: models.BreakQuerySet
) -> str:
    """
    Get part of a potential error message stating the times of the
    breaks that an updated break causes clashes with.
    """
    break_clashes = clash_filters.filter_queryset_for_clashes(
        queryset=check_against_breaks, time_of_week=time_of_week
    )
    if break_clashes:
        return ", ".join(
            [
                f'{break_.starts_at.strftime("%H:%M")}-{break_.ends_at.strftime("%H:%M")}'
                for break_ in break_clashes
            ]
        )
    return ""


def _get_slot_clash_str(
    time_of_week: clash_filters.TimeOfWeek,
    check_against_slots: models.TimetableSlotQuerySet,
) -> str:
    """
    Get part of a potential error message stating the times of the
    slots that an updated break causes clashes with.
    """
    slot_clashes = clash_filters.filter_queryset_for_clashes(
        queryset=check_against_slots, time_of_week=time_of_week
    )
    if slot_clashes:
        return ", ".join(
            [
                f'{slot.starts_at.strftime("%H:%M")}-{slot.ends_at.strftime("%H:%M")}'
                for slot in slot_clashes
            ]
        )
    return ""
