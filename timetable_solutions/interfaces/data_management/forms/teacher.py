"""Forms relating to the Teacher model."""

from django import forms as django_forms

from data import models
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
        label="Firstname",
    )

    title = django_forms.CharField(
        required=True,
        label="Firstname",
    )


class TeacherUpdate(_TeacherCreateUpdateBase):
    """Form to update a teacher with."""

    def __init__(self, *args: object, **kwargs: models.Teacher) -> None:
        """Set the initial displayed values to the teacher's attribute values."""
        teacher: models.Teacher = kwargs.pop("teacher")
        self.base_fields["firstname"].initial = teacher.firstname
        self.base_fields["surname"].initial = teacher.surname
        self.base_fields["title"].initial = teacher.title
        super().__init__(*args, **kwargs)


class TeacherCreate(_TeacherCreateUpdateBase):
    teacher_id = django_forms.IntegerField(
        required=True,
        label="Teacher ID",
        help_text="Unique identifier to be used for this teacher",
    )

    def clean_teacher_id(self) -> int:
        """Check the given teacher id does not already exist for the school."""
        teacher_id = self.cleaned_data.get("teacher_id")
        try:
            models.Teacher.objects.get_individual_teacher(
                school_id=self.school_id, teacher_id=teacher_id
            )
            raise django_forms.ValidationError(
                f"Teacher with id: {teacher_id} already exists!"
            )
        except models.Teacher.DoesNotExist:
            return teacher_id
