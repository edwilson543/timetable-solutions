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


class TimetableSlotSearch(django_forms.Form):
    slot_id = django_forms.IntegerField(required=False, label="Slot ID")

    day_of_week = django_forms.TypedChoiceField(
        required=False, choices=constants.Day.choices, label="Day of week", coerce=int
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

    def clean_slot_id(self) -> int | None:
        if not (slot_id := self.cleaned_data.get("slot_id", None)):
            return None
        try:
            models.TimetableSlot.objects.get_individual_timeslot(
                school_id=self.school_id, slot_id=slot_id
            )
            return slot_id
        except models.TimetableSlot.DoesNotExist:
            raise django_forms.ValidationError(
                f"No timetable slot with id: {slot_id} exists!"
            )


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


class TimetableSlotUpdateYearGroups(django_forms.Form):
    """
    Form for updating the year groups relevant to a particular timetable slot.
    """

    # TODO -> use a model multiple choice field


class TimetableSlotUpdateTimings(_TimetableSlotCreateUpdateBase):
    """
    Form to update the time of a timetable slots with.
    """

    def __init__(self, *args: object, **kwargs: Any) -> None:
        slot = kwargs.pop("slot")
        self.slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=kwargs["school_id"], slot_id=slot.slot_id
        )
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        self.raise_if_slot_doesnt_end_after_starting()
        self._raise_if_updated_slot_would_produce_a_clash()
        return self.cleaned_data

    def _raise_if_updated_slot_would_produce_a_clash(self) -> None:
        new_time_of_week = clash_filters.TimeOfWeek(
            starts_at=self.cleaned_data["starts_at"],
            ends_at=self.cleaned_data["ends_at"],
            day_of_week=self.cleaned_data["day_of_week"],
        )

        slot_clash_str = self._get_slot_clash_str(new_time_of_week)
        break_clash_str = self._get_break_clash_str(new_time_of_week)

        if slot_clash_str and break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be updated to this time since at least one of its assigned year groups has a "
                f"slot(s) at {slot_clash_str} and break(s) at {break_clash_str} clashing with this time."
            )
        elif slot_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be updated to this time since at least one of its assigned year groups has a "
                f"slot(s) at {slot_clash_str} clashing with this time."
            )
        elif break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be updated to this time since at least one of its assigned year groups has a "
                f"break(s) at {break_clash_str} clashing with this time."
            )

    def _get_slot_clash_str(self, new_time_of_week: clash_filters.TimeOfWeek) -> str:
        all_slots = models.TimetableSlot.objects.filter(
            relevant_year_groups__in=self.slot.relevant_year_groups.all()
        )
        slot_clashes = clash_filters.filter_queryset_for_clashes(
            queryset=all_slots, time_of_week=new_time_of_week
        )
        if slot_clashes:
            return ", ".join(
                [f"{slot.starts_at}-{slot.ends_at}" for slot in slot_clashes]
            )
        return ""

    def _get_break_clash_str(self, new_time_of_week: clash_filters.TimeOfWeek) -> str:
        breaks = models.Break.objects.filter(
            relevant_year_groups__in=self.slot.relevant_year_groups.all()
        )
        break_clashes = clash_filters.filter_queryset_for_clashes(
            queryset=breaks, time_of_week=new_time_of_week
        )
        if break_clashes:
            return ", ".join(
                [f"{break_.starts_at}-{break_.ends_at}" for break_ in break_clashes]
            )
        return ""


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

        slot_clash_str = self._get_slot_clash_str(time_of_week)
        break_clash_str = self._get_break_clash_str(time_of_week)

        if slot_clash_str and break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to all year groups since your school has a "
                f"slot(s) at {slot_clash_str} and break(s) at {break_clash_str} clashing with this time."
            )
        elif slot_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to all year groups since your school has a "
                f"slot(s) at {slot_clash_str} clashing with this time."
            )
        elif break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to all year groups since your school has a "
                f"break(s) at {break_clash_str} clashing with this time."
            )

    def _get_slot_clash_str(self, time_of_week: clash_filters.TimeOfWeek) -> str:
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        slot_clashes = clash_filters.filter_queryset_for_clashes(
            queryset=all_slots, time_of_week=time_of_week
        )
        if slot_clashes:
            return ", ".join(
                [f"{slot.starts_at}-{slot.ends_at}" for slot in slot_clashes]
            )
        return ""

    def _get_break_clash_str(self, time_of_week: clash_filters.TimeOfWeek) -> str:
        all_breaks = models.Break.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        break_clashes = clash_filters.filter_queryset_for_clashes(
            queryset=all_breaks, time_of_week=time_of_week
        )
        if break_clashes:
            return ", ".join(
                [f"{break_.starts_at}-{break_.ends_at}" for break_ in break_clashes]
            )
        return ""
