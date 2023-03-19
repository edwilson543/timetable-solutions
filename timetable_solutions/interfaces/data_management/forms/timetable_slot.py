"""
Forms relating to the TimetableSlot model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from data import constants, models
from domain.solver.filters import clashes as clash_filters
from interfaces.data_management.forms import base_forms


class _TimetableSlotCreateUpdateBase(base_forms.CreateUpdate):
    """
    Base form for the timetable slot create and update forms.
    """

    day_of_week = django_forms.ChoiceField(
        required=True, choices=constants.Day.choices, label="Day of week"
    )

    starts_at = django_forms.TimeField(required=True, label="When the slot starts")

    ends_at = django_forms.TimeField(required=True, label="When the slot ends")

    def raise_if_slot_doesnt_end_after_starting(self) -> None:
        if self.cleaned_data["starts_at"] >= self.cleaned_data["ends_at"]:
            raise django_forms.ValidationError(
                "The slot must end after it has started!"
            )


class TimetableSlotCreate(_TimetableSlotCreateUpdateBase):
    """
    Form to create individual timetable slots with.
    """

    slot_id = django_forms.IntegerField(
        min_value=1,
        required=False,
        label="Slot ID",
        help_text="Unique identifier to be used for this slot. "
        "If unspecified we will use the next ID available.",
    )

    relevant_to_all_year_groups = django_forms.BooleanField(
        required=False,
        label="Relevant to all year groups",
        help_text="Select this if this timetable slot is relevant to all of your year groups. "
        "You can change the year groups this timetable slot is for once created.",
    )

    field_order = [
        "slot_id",
        "day_of_week",
        "starts_at",
        "ends_at",
        "relevant_to_all_year_groups",
    ]

    def clean(self) -> dict[str, Any]:
        self.raise_if_slot_doesnt_end_after_starting()
        if self.cleaned_data.get("relevant_to_all_year_groups", False):
            self._raise_if_new_slot_would_produce_a_clash()
        return self.cleaned_data

    def _raise_if_new_slot_would_produce_a_clash(self) -> None:
        time_of_week = clash_filters.TimeOfWeek(
            starts_at=self.cleaned_data["starts_at"],
            ends_at=self.cleaned_data["ends_at"],
            day_of_week=self.cleaned_data["day_of_week"],
        )

        # Check no clashing slots
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        slot_clashes = clash_filters.filter_queryset_for_clashes(
            queryset=all_slots, time_of_week=time_of_week
        )

        # Check no clashing breaks
        all_breaks = models.Break.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        break_clashes = clash_filters.filter_queryset_for_clashes(
            queryset=all_breaks, time_of_week=time_of_week
        )

        # Raise appropriate error message
        if slot_clashes:
            slot_clash_str = ", ".join(
                [f"{slot.starts_at}-{slot.ends_at}" for slot in slot_clashes]
            )
        if break_clashes:
            break_clash_str = ", ".join(
                [f"{break_.starts_at}-{break_.ends_at}" for break_ in break_clashes]
            )

        if slot_clashes and break_clashes:
            raise django_forms.ValidationError(
                f"This slot cannot be assigned to all year groups since your school has "
                f"slot(s) at {slot_clash_str} and break(s) at {break_clash_str} clashing with this time."
            )
        elif slot_clashes:
            raise django_forms.ValidationError(
                f"This slot cannot be assigned to all year groups since your school has "
                f"slot(s) at {slot_clash_str} clashing with this time."
            )
        elif break_clashes:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to all year groups since your school has "
                f"break(s) at {break_clash_str} clashing with this time."
            )
