"""
Module defining constants related to example files
"""

# Standard library imports
from enum import StrEnum
from pathlib import Path

# Django imports
from django.conf import settings


class ExampleFile(StrEnum):
    """
    Enumeration of all the example files that can be downloaded by users, and construction of their respective urls.
    """
    PUPILS = "example_pupils.csv"
    TEACHERS = "example_teachers.csv"
    CLASSROOMS = "example_classrooms.csv"
    TIMETABLE = "example_timetable.csv"
    UNSOLVED_CLASS = "example_class_requirements.csv"
    FIXED_CLASS = "example_fixed_classes.csv"

    @property
    def filepath(self) -> Path:
        """
        Property indicating the absolute path the example file is stored at on the local file system.
        """
        path = settings.BASE_DIR / settings.MEDIA_ROOT / "example_files" / self.value
        return path
