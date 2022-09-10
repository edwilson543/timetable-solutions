"""
Module containing forms that allow users to upload their school_id data (pupil lists, timetable structure etc.)
These get uploaded as csv files and then used to populate the relevant model in the database using the ORM.
"""

# Django imports
from django.forms import Form, FileField


class TeacherListUploadForm(Form):
    """Form containing an individual upload slot for the list of teachers."""
    teacher_list = FileField(allow_empty_file=False, label="")


class PupilListUploadForm(Form):
    """Form containing an individual upload slot for the list of pupils."""
    pupil_list = FileField(allow_empty_file=False, label="")


class ClassroomListUploadForm(Form):
    """Form containing an individual upload slot for the list of pupils."""
    classroom_list = FileField(allow_empty_file=False, label="")


class TimetableStructureUploadForm(Form):
    """Form containing an individual upload slot for the structure of the timetable."""
    timetable_structure = FileField(allow_empty_file=False, label="")


class UnsolvedClassUploadForm(Form):
    """Form containing an individual upload slot for the classes that must be taught, and associated details."""
    unsolved_classes = FileField(allow_empty_file=False, label="")


class FixedClassUploadForm(Form):
    """Form containing an individual upload slot for 'fixed classes' i.e. classes which must occur at certain times."""
    fixed_classes = FileField(allow_empty_file=False, label="")
