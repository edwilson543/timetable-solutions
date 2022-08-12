"""
Module containing forms that allow users to upload their school data (pupil lists, timetable structure etc.)
and specify their requirements for generating timetable solutions.
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
