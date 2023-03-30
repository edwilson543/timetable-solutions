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
        queryset=models.YearGroup.objects.none(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Get and set the year group choices.
        """
        self.school_id = kwargs.pop("school_id")
        super().__init__(*args, **kwargs)

        year_groups = models.YearGroup.objects.get_all_instances_for_school(
            school_id=self.school_id
        ).order_by("year_group_name")
        self.fields["year_group"].queryset = year_groups

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


class TimetableSlotUpdateYearGroups(django_forms.Form):
    """
    Form for updating the year groups relevant to a particular timetable slot.
    """

    relevant_year_groups = django_forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.TimetableSlot.objects.none(),
        label="Select the year groups that this timetable slot is relevant to",
    )

    def __init__(self, *args: object, **kwargs: Any) -> None:
        self.school_id = kwargs.pop("school_id")
        slot = kwargs.pop("slot")
        super().__init__(*args, **kwargs)

        self.slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=self.school_id, slot_id=slot.slot_id
        )

        # Set all this school's year groups as the options
        self.fields[
            "relevant_year_groups"
        ].queryset = models.YearGroup.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        # ...but only the year groups currently assigned to this slot as the initial values
        self.fields[
            "relevant_year_groups"
        ].initial = slot.relevant_year_groups.all().values_list("pk", flat=True)

    def clean(self) -> dict[str, Any]:
        """
        Check the slot can be made relevant to the selected year groups
        """
        self._raise_if_no_year_group_selected()
        self._raise_if_clashes_produced_for_a_year_group()
        self._raise_if_slot_in_use_for_a_lesson()
        return self.cleaned_data

    def _raise_if_no_year_group_selected(self) -> None:
        if not self.cleaned_data["relevant_year_groups"]:
            raise django_forms.ValidationError(
                "You must select at least one year group!"
            )

    def _raise_if_clashes_produced_for_a_year_group(self) -> None:
        time_of_week = clash_filters.TimeOfWeek.from_slot(self.slot)

        # Check for clashes with slots
        check_against_slots = models.TimetableSlot.objects.filter(
            relevant_year_groups__in=self.cleaned_data["relevant_year_groups"]
        ).exclude(slot_id=self.slot.slot_id)
        slot_clash_str = _get_slot_clash_str(
            time_of_week=time_of_week, check_against_slots=check_against_slots
        )

        # Check for clashes with breaks
        check_against_breaks = models.Break.objects.filter(
            relevant_year_groups__in=self.cleaned_data["relevant_year_groups"]
        )
        break_clash_str = _get_break_clash_str(
            time_of_week=time_of_week, check_against_breaks=check_against_breaks
        )

        if slot_clash_str and break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to these year groups, since at least one year group has a "
                f"slot at {slot_clash_str} and break at {break_clash_str} clashing with this time."
            )
        elif slot_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to these year groups, since at least one year group has a "
                f"slot at {slot_clash_str} clashing with this time."
            )
        elif break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to these year groups, since at least one year group has a "
                f"break at {break_clash_str} clashing with this time."
            )

    def _raise_if_slot_in_use_for_a_lesson(self) -> None:
        """
        If trying to unassign a slot as relevant to a year group but there is already a lesson
        using this slot for that year group, then raise.
        """
        selected_ygs = self.cleaned_data["relevant_year_groups"]
        removed_year_groups = [
            # Note qs.difference(other_qs) not available for SQLite
            yg
            for yg in self.slot.relevant_year_groups.all()
            if yg not in selected_ygs
        ]
        if removed_year_groups:
            lessons = self.slot.get_all_lessons()
            protected_year_groups = [
                lesson.get_associated_year_group() for lesson in lessons
            ]
            invalid_removals = [
                yg for yg in removed_year_groups if yg in protected_year_groups
            ]
            if invalid_removals:
                invalid_removals_str = ", ".join(
                    yg.year_group_name for yg in invalid_removals
                )
                raise django_forms.ValidationError(
                    f"Cannot unassign year group(s) {invalid_removals_str} from this slot since each "
                    "of them has at least one lesson using this slot."
                )


class _TimetableSlotCreateUpdateBase(base_forms.CreateUpdate):
    """
    Base form for the timetable slot create and update forms.
    """

    day_of_week = django_forms.TypedChoiceField(
        required=True, choices=constants.Day.choices, label="Day of week", coerce=int
    )

    starts_at = django_forms.TimeField(required=True, label="When the slot starts")

    ends_at = django_forms.TimeField(required=True, label="When the slot ends")

    def raise_if_slot_doesnt_end_after_starting(self) -> None:
        if self.cleaned_data["starts_at"] >= self.cleaned_data["ends_at"]:
            raise django_forms.ValidationError(
                "The slot must end after it has started!"
            )


class TimetableSlotUpdateTimings(_TimetableSlotCreateUpdateBase):
    """
    Form to update the time of a timetable slots with.
    """

    def __init__(self, *args: object, **kwargs: Any) -> None:
        self.slot = kwargs.pop("slot")
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

        # Check for clashes with slots
        check_against_slots = models.TimetableSlot.objects.filter(
            relevant_year_groups__in=self.slot.relevant_year_groups.all()
        ).exclude(slot_id=self.slot.slot_id)
        slot_clash_str = _get_slot_clash_str(
            time_of_week=new_time_of_week, check_against_slots=check_against_slots
        )

        # Check for clashes with breaks
        check_against_breaks = models.Break.objects.filter(
            relevant_year_groups__in=self.slot.relevant_year_groups.all()
        )
        break_clash_str = _get_break_clash_str(
            time_of_week=new_time_of_week, check_against_breaks=check_against_breaks
        )

        if slot_clash_str and break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be updated to this time since at least one of its assigned year groups has a "
                f"slot at {slot_clash_str} and break at {break_clash_str} clashing with this time."
            )
        elif slot_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be updated to this time since at least one of its assigned year groups has a "
                f"slot at {slot_clash_str} clashing with this time."
            )
        elif break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be updated to this time since at least one of its assigned year groups has a "
                f"break at {break_clash_str} clashing with this time."
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
        help_text="Select this if the slot is for all of your year groups. "
        "You can update the year groups this timetable slot is relevant to once created.",
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

        # Check for clashes with slots
        check_against_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        slot_clash_str = _get_slot_clash_str(
            time_of_week=time_of_week, check_against_slots=check_against_slots
        )

        # Check for clashes with breaks
        check_against_breaks = models.Break.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        break_clash_str = _get_break_clash_str(
            time_of_week=time_of_week, check_against_breaks=check_against_breaks
        )

        if slot_clash_str and break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to all year groups since your school has a "
                f"slot at {slot_clash_str} and break at {break_clash_str} clashing with this time."
            )
        elif slot_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to all year groups since your school has a "
                f"slot at {slot_clash_str} clashing with this time."
            )
        elif break_clash_str:
            raise django_forms.ValidationError(
                "This slot cannot be assigned to all year groups since your school has a "
                f"break at {break_clash_str} clashing with this time."
            )


def _get_slot_clash_str(
    time_of_week: clash_filters.TimeOfWeek,
    check_against_slots: models.TimetableSlotQuerySet,
) -> str:
    """
    Get part of a potential error message stating the times of the
    slots that an updated slot causes clashes with.
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


def _get_break_clash_str(
    time_of_week: clash_filters.TimeOfWeek, check_against_breaks: models.BreakQuerySet
) -> str:
    """
    Get part of a potential error message stating the times of the
    breaks that an updated slot causes clashes with.
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
