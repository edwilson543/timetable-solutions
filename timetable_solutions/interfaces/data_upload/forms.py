"""
Module containing forms that allow users to upload their school_id data (pupil lists, timetable structure etc.)
These get uploaded as csv files and then used to populate the relevant model in the database using the ORM.

Note that none of the file_field_names actually matter, but are accessed dynamically when accessing the forms,
hence their inclusion.
"""

# Standard library imports
from typing import Union

# Django imports
from django import forms as django_forms


class TeacherListUpload(django_forms.Form):
    """Form containing an individual upload slot for the list of teachers."""

    teacher_list = django_forms.FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "teacher_list"


class ClassroomListUpload(django_forms.Form):
    """Form containing an individual upload slot for the list of classrooms."""

    classroom_list = django_forms.FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "classroom_list"


class YearGroupUpload(django_forms.Form):
    """Form containing an individual upload slot for the list of year groups"""

    year_group_list = django_forms.FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "year_group_list"


class PupilListUpload(django_forms.Form):
    """Form containing an individual upload slot for the list of pupils."""

    pupil_list = django_forms.FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "pupil_list"


class TimetableStructureUpload(django_forms.Form):
    """Form containing an individual upload slot for the structure of the timetable."""

    timetable_structure = django_forms.FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "timetable_structure"


class LessonUpload(django_forms.Form):
    """Form containing an individual upload slot for the lessons that must be taught, and associated details."""

    lessons = django_forms.FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "lessons"


class BreakUpload(django_forms.Form):
    """Form containing an individual upload slot for the breaks model."""

    breaks = django_forms.FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "breaks"


# Type hint to use when referencing one of the above collection of forms
UploadForm = Union[
    TeacherListUpload,
    ClassroomListUpload,
    YearGroupUpload,
    PupilListUpload,
    TimetableStructureUpload,
    LessonUpload,
    BreakUpload,
]
