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
    # Users app
    LOGIN = "login"
    LOGOUT = "logout"

    # Data upload app
    FILE_UPLOAD_PAGE = "file_upload_page"
    TEACHER_LIST_UPLOAD = "teacher_list"
    PUPIL_LIST_UPLOAD = "pupil_list"
    CLASSROOM_LIST_UPLOAD = "classroom_list"
    TIMETABLE_STRUCTURE_UPLOAD = "timetable_structure"
    UNSOLVED_CLASSES_UPLOAD = "unsolved_classes"
    FIXED_CLASSES_UPLOAD = "fixed_classes"

    # Create timetables app
    CREATE_TIMETABLES = "create_timetables"

    # View timetables app
    VIEW_TIMETABLES_DASH = "selection_dashboard"
    TEACHERS_NAVIGATOR = "teachers_navigator"
    TEACHER_TIMETABLE = "teacher_timetable_view"  # Note reverse also requires a teacher id
    PUPILS_NAVIGATOR = "pupils_navigator"
    PUPIL_TIMETABLE = "pupil_timetable_view"  # Note reverse also requires a pupil id
