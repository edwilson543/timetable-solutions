"""
Module defining constants relating to urls.
"""

# Standard library imports
from enum import Enum


class UrlName(Enum):
    """
    Enumeration of ALL url shortcut names in the entire project.

    This is the single place where url names are written in python - elsewhere, they are accessed via this Enum, for
    example whenever urls.reverse is called, the argument is accessed from this Enum. Also in all apps' url dispatchers.
    Note however that some django html templates access the string versions via the {% url <url_name> %} tag, so these
    would need updating.
    """
    # Users app
    DASHBOARD = "dashboard"
    LOGIN = "login"
    LOGOUT = "logout"
    PROFILE_REGISTRATION = "profile_registration"
    REGISTER = "register"
    REGISTER_PIVOT = "registration_pivot"
    SCHOOL_REGISTRATION = "school_registration"

    # Data upload app
    FILE_UPLOAD_PAGE = "file_upload_page"

    # File upload urls
    CLASSROOM_LIST_UPLOAD = "classroom_upload"
    FIXED_CLASSES_UPLOAD = "fixed_class_upload"
    PUPIL_LIST_UPLOAD = "pupil_upload"
    TEACHER_LIST_UPLOAD = "teacher_upload"
    TIMETABLE_STRUCTURE_UPLOAD = "timetable_upload"
    UNSOLVED_CLASSES_UPLOAD = "unsolved_class_upload"

    # File upload reset urls
    CLASSROOM_LIST_RESET = "classroom_reset"
    FIXED_CLASSES_RESET = "fixed_class_reset"
    PUPIL_LIST_RESET = "pupil_reset"
    TEACHER_LIST_RESET = "teacher_reset"
    TIMETABLE_STRUCTURE_RESET = "timetable_reset"
    UNSOLVED_CLASSES_RESET = "unsolved_class_reset"

    # Create timetables app
    CREATE_TIMETABLES = "create_timetables"

    # View timetables app
    PUPILS_NAVIGATOR = "pupils_navigator"
    PUPIL_TIMETABLE = "pupil_timetable"  # Note reverse also requires a pupil id
    TEACHERS_NAVIGATOR = "teachers_navigator"
    TEACHER_TIMETABLE = "teacher_timetable"  # Note reverse also requires a teacher id
    VIEW_TIMETABLES_DASH = "selection_dashboard"
