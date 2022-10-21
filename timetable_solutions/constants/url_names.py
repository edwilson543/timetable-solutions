"""
Module defining constants relating to urls.
"""

# Standard library imports
from enum import Enum


class UrlName(Enum):
    """
    Enumeration of ALL url shortcut names in the entire project.
    This is the single place where url names are written manually - elsewhere, they are accessed via this Enum.
    """
    # Data upload app
    FILE_UPLOAD_PAGE = "file_upload_page"
    TEACHER_LIST_UPLOAD = "teacher_list"
    PUPIL_LIST_UPLOAD = "pupil_list"
    CLASSROOM_LIST_UPLOAD = "classroom_list"
    TIMETABLE_STRUCTURE_UPLOAD = "timetable_structure"
    UNSOLVED_CLASSES_UPLOAD = "unsolved_classes"
    FIXED_CLASSES_UPLOAD = "fixed_classes"
