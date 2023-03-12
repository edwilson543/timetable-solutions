"""Forms relating to the Teacher model."""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from domain.data_management.teachers import queries
from interfaces.data_management.forms import base_forms


class TeacherSearch(django_forms.Form):
    """
    Single field search form for the teacher model.
    """

    search_term = django_forms.CharField(
        required=True,
        label="Search term",
        initial="",
        help_text="Search for a teacher by name or id.",
        error_messages={"required": "Please enter a search term!"},
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if kwargs.get("search_help_text"):
            self.base_fields["search_term"].help_text = kwargs.pop("search_help_text")
        super().__init__(*args, **kwargs)

    def clean_search_term(self) -> str:
        """Prevent single letter searches."""
        if search_term := self.cleaned_data.get("search_term"):
            try:
                int(search_term)
            except ValueError:
                if len(search_term) < 2:
                    raise django_forms.ValidationError(
                        "Non-numeric search terms must be more than one character!"
                    )
        return search_term


class _TeacherCreateUpdateBase(base_forms.CreateUpdate):
    """Base form for the teacher create and update forms."""

    firstname = django_forms.CharField(
        required=True,
        label="Firstname",
    )

    surname = django_forms.CharField(
        required=True,
        label="Surname",
    )

    title = django_forms.CharField(
        required=True,
        label="Title",
    )


class TeacherUpdate(_TeacherCreateUpdateBase):
    """Form to update a teacher with."""

    pass


class TeacherCreate(_TeacherCreateUpdateBase):
    teacher_id = django_forms.IntegerField(
        required=False,
        label="Teacher ID",
        help_text="Unique identifier to be used for this teacher. "
        "If unspecified we will use the next ID available.",
    )

    field_order = ["teacher_id", "firstname", "surname", "title"]

    def clean_teacher_id(self) -> int:
        """Check the given teacher id does not already exist for the school."""
        teacher_id = self.cleaned_data.get("teacher_id")
        if queries.get_teacher_for_school(
            school_id=self.school_id, teacher_id=teacher_id
        ):
            next_available_id = queries.get_next_teacher_id_for_school(
                school_id=self.school_id
            )
            raise django_forms.ValidationError(
                f"Teacher with id: {teacher_id} already exists! "
                f"The next available id is: {next_available_id}"
            )
        return teacher_id
