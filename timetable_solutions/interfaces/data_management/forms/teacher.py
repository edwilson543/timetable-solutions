"""Forms relating to the Teacher model."""

from typing import Any

from django import forms as django_forms

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
        required=True,
        label="Teacher ID",
        help_text="Unique identifier to be used for this teacher",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set the next available ID as the initial teacher_id."""
        super().__init__(*args, **kwargs)
        self.base_fields["teacher_id"].initial = queries.get_next_teacher_id_for_school(
            school_id=self.school_id
        )

    def clean_teacher_id(self) -> int:
        """Check the given teacher id does not already exist for the school."""
        teacher_id = self.cleaned_data.get("teacher_id")
        if queries.get_teacher_for_school(
            school_id=self.school_id, teacher_id=teacher_id
        ):
            raise django_forms.ValidationError(
                f"Teacher with id: {teacher_id} already exists! "
                f"The next available id is: {self.base_fields['teacher_id'].initial}"
            )
        return teacher_id
