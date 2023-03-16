"""
Forms relating to the Teacher model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from data import constants, models
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
        if self.cleaned_data.get("relevant_to_all_year_groups", False):
            existing_slots = models.TimetableSlot.objects.get_all_instances_for_school(
                school_id=self.school_id
            )
        return self.cleaned_data
