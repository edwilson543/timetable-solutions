"""
Module containing forms that allow users to upload their school_id data (pupil lists, timetable structure etc.)
These get uploaded as csv files and then used to populate the relevant model in the database using the ORM.
"""

# Standard library imports
from typing import Union

# Django imports
from django.forms import Form, FileField


class TeacherListUpload(Form):
    """Form containing an individual upload slot for the list of teachers."""
    teacher_list = FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "teacher_list"


class PupilListUpload(Form):
    """Form containing an individual upload slot for the list of pupils."""
    pupil_list = FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "pupil_list"


class ClassroomListUpload(Form):
    """Form containing an individual upload slot for the list of pupils."""
    classroom_list = FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "classroom_list"


class TimetableStructureUpload(Form):
    """Form containing an individual upload slot for the structure of the timetable."""
    timetable_structure = FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "timetable_structure"


class UnsolvedClassUpload(Form):
    """Form containing an individual upload slot for the classes that must be taught, and associated details."""
    unsolved_classes = FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "unsolved_classes"


class FixedClassUpload(Form):
    """Form containing an individual upload slot for 'fixed classes' i.e. classes which must occur at certain times."""
    fixed_classes = FileField(allow_empty_file=False, label="")

    class Meta:
        file_field_name = "fixed_classes"


# Type hint to use when generically referencing the above collection of forms
FormSubclass = Union[TeacherListUpload, PupilListUpload, ClassroomListUpload, TimetableStructureUpload,
                     UnsolvedClassUpload, FixedClassUpload]
