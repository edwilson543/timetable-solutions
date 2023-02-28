"""Forms relating to the Teacher model."""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from data import models
from domain.data_management.teachers import queries

from . import base_forms


class TeacherSearch(base_forms.Search):
    """Single field search form for the teacher model."""

    pass


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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set the next available ID as the initial teacher_id."""
        super().__init__(*args, **kwargs)

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


class TeacherDelete(base_forms.Delete):
    """Form to delete a single teacher with."""

    model_instance: models.Teacher

    def clean(self) -> dict[str, Any]:
        """Validate that the teacher has no lessons."""
        if self.model_instance.lessons.exists():
            raise django_forms.ValidationError(
                "This teacher is still assigned to at least one lesson!\n"
                "To delete this teacher, first delete or reassign their lessons"
            )
        return self.cleaned_data
