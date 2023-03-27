"""
Forms relating to the Break model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms
from django.db import models as django_models

# Local application imports
from data import constants, models
from domain.solver.filters import clashes as clash_filters
from domain.solver.queries import teacher as teacher_solver_queries
from interfaces.data_management.forms import base_forms


class BreakSearch(django_forms.Form):
    """
    Search form for the Break model.
    """

    search_term = django_forms.CharField(
        required=False, label="Search for a break by name or id"
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
        search_term = self.cleaned_data.get("search_term", None)
        day = self.cleaned_data.get("day_of_week", None)
        year_group = self.cleaned_data["year_group"]
        if not (search_term or day or year_group):
            raise django_forms.ValidationError("Please enter a search term!")

        return self.cleaned_data


class BreakUpdateYearGroups(django_forms.Form):
    """
    Form for updating the year groups relevant to a particular break.
    """

    relevant_year_groups = django_forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.TimetableSlot.objects.none(),
        label="Select the year groups that this break is relevant to",
    )

    def __init__(self, *args: object, **kwargs: Any) -> None:
        self.school_id = kwargs.pop("school_id")
        break_ = kwargs.pop("break_")
        super().__init__(*args, **kwargs)

        # Set the break we are updating
        self.break_ = models.Break.objects.get(
            school_id=self.school_id, break_id=break_.break_id
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
        ].initial = break_.relevant_year_groups.all().values_list("pk", flat=True)

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


class _BreakCreateUpdateBase(base_forms.CreateUpdate):
    """
    Base form for the break create and update forms.
    """

    break_name = django_forms.CharField(
        required=True,
        label="Break name",
    )

    day_of_week = django_forms.TypedChoiceField(
        required=True, choices=constants.Day.choices, label="Day of week", coerce=int
    )

    starts_at = django_forms.TimeField(required=True, label="When the break starts")

    ends_at = django_forms.TimeField(required=True, label="When the break ends")

    def raise_if_break_doesnt_end_after_starting(self) -> None:
        if self.cleaned_data["starts_at"] >= self.cleaned_data["ends_at"]:
            raise django_forms.ValidationError(
                "The break must end after it has started!"
            )


class BreakUpdateTimings(_BreakCreateUpdateBase):
    """
    Form to update the name / time of a break with.
    """

    def __init__(self, *args: object, **kwargs: Any) -> None:
        self.break_ = kwargs.pop("break_")
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        self.raise_if_break_doesnt_end_after_starting()
        self._raise_if_updated_break_would_produce_a_clash()
        return self.cleaned_data

    def _raise_if_updated_break_would_produce_a_clash(self) -> None:
        new_time_of_week = clash_filters.TimeOfWeek(
            starts_at=self.cleaned_data["starts_at"],
            ends_at=self.cleaned_data["ends_at"],
            day_of_week=self.cleaned_data["day_of_week"],
        )

        # Check for clashes with breaks
        check_against_breaks = models.Break.objects.filter(
            django_models.Q(
                relevant_year_groups__in=self.break_.relevant_year_groups.all()
            )
            | django_models.Q(teachers__in=self.break_.teachers.all())
        ).exclude(break_id=self.break_.break_id)
        break_clash_str = _get_break_clash_str(
            time_of_week=new_time_of_week, check_against_breaks=check_against_breaks
        )

        # Check for clashes with slots
        check_against_slots = models.TimetableSlot.objects.filter(
            relevant_year_groups__in=self.break_.relevant_year_groups.all()
        )
        slot_clash_str = _get_slot_clash_str(
            time_of_week=new_time_of_week, check_against_slots=check_against_slots
        )

        if break_clash_str and slot_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be updated to this time since at least one of its assigned year groups or teachers "
                f"has a slot at {slot_clash_str} and break at {break_clash_str} clashing with this time."
            )
        elif break_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be updated to this time since at least one of its assigned year groups has a "
                f"break at {break_clash_str} clashing with this time."
            )
        elif slot_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be updated to this time since at least one of its assigned year groups has a "
                f"slot at {slot_clash_str} clashing with this time."
            )


class BreakCreate(_BreakCreateUpdateBase):
    """
    Form to create individual breaks with.
    """

    break_id = django_forms.CharField(
        required=True,
        label="Break ID",
        help_text="Unique identifier to be used for this break.",
    )

    relevant_to_all_year_groups = django_forms.BooleanField(
        required=False,
        label="Relevant to all year groups",
        help_text="Select this if the break is for all of your year groups. "
        "You can update the year groups this break is relevant to once created.",
    )

    relevant_to_all_teachers = django_forms.BooleanField(
        required=False,
        label="Relevant to all teachers",
        help_text="Select this if the break is for all of your teachers. "
        "You can update the teachers this break is relevant to once created.",
    )

    field_order = [
        "break_id",
        "break_name",
        "day_of_week",
        "starts_at",
        "ends_at",
        "relevant_to_all_year_groups",
    ]

    def clean(self) -> dict[str, Any]:
        self.raise_if_break_doesnt_end_after_starting()

        time_of_week = clash_filters.TimeOfWeek(
            starts_at=self.cleaned_data["starts_at"],
            ends_at=self.cleaned_data["ends_at"],
            day_of_week=self.cleaned_data["day_of_week"],
        )
        if self.cleaned_data.get("relevant_to_all_year_groups", False):
            self._raise_if_new_slot_would_produce_a_clash(time_of_week)
        if self.cleaned_data.get("relevant_to_all_teachers", False):
            self._raise_if_new_slot_would_produce_teacher_clash(time_of_week)
        return self.cleaned_data

    def _raise_if_new_slot_would_produce_teacher_clash(
        self, time_of_week: clash_filters.TimeOfWeek
    ) -> None:
        # Get the breaks that have at least one teacher
        check_against_breaks = models.Break.objects.annotate(
            n_teachers=django_models.Count("teachers")
        ).filter(
            django_models.Q(school_id=self.school_id)
            & django_models.Q(n_teachers__gt=0)
        )
        break_clash_str = _get_break_clash_str(
            time_of_week=time_of_week, check_against_breaks=check_against_breaks
        )
        if break_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be assigned to all teachers since your school has a break "
                f" at {break_clash_str} clashing with this time."
            )

    def _raise_if_new_slot_would_produce_a_clash(
        self, time_of_week: clash_filters.TimeOfWeek
    ) -> None:
        # Check for clashes with breaks
        check_against_breaks = models.Break.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        break_clash_str = _get_break_clash_str(
            time_of_week=time_of_week, check_against_breaks=check_against_breaks
        )

        # Check for clashes with slots
        check_against_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        slot_clash_str = _get_slot_clash_str(
            time_of_week=time_of_week, check_against_slots=check_against_slots
        )

        if break_clash_str and slot_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be assigned to all year groups since your school has a "
                f"slot at {slot_clash_str} and break at {break_clash_str} clashing with this time."
            )
        elif break_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be assigned to all year groups since your school has a "
                f"break at {break_clash_str} clashing with this time."
            )
        elif slot_clash_str:
            raise django_forms.ValidationError(
                "This break cannot be assigned to all year groups since your school has a "
                f"slot at {slot_clash_str} clashing with this time."
            )


class BreakAddTeacher(django_forms.Form):
    teacher = django_forms.ModelChoiceField(
        required=True,
        label="Add a teacher to this break",
        empty_label="",
        queryset=models.Teacher.objects.none(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.break_ = kwargs.pop("break_")
        super().__init__(*args, **kwargs)

        # Set the teachers that can be added as those
        # not already assigned to this break
        exclude_pks = self.break_.teachers.values_list("pk", flat=True)
        teachers = (
            models.Teacher.objects.filter(school=self.break_.school)
            .exclude(pk__in=exclude_pks)
            .order_by("surname")
        )
        if teachers:
            self.fields["teacher"].queryset = teachers
        else:
            self.fields["teacher"].disabled = True
            self.fields[
                "teacher"
            ].help_text = "All your teachers are currently assigned to this break"

    def clean(self) -> dict[str, Any]:
        teacher = self.cleaned_data["teacher"]
        if teacher_solver_queries.check_if_teacher_busy_at_time(
            teacher=teacher,
            starts_at=self.break_.starts_at,
            ends_at=self.break_.ends_at,
            day_of_week=self.break_.day_of_week,
        ):
            raise django_forms.ValidationError(
                "This teacher is already busy during this break!"
            )
        return self.cleaned_data


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
