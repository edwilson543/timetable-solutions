"""
Module defining constants relating to urls.
"""

# Standard library imports
from enum import Enum


class UrlName(Enum):
    """
    Enumeration of ALL url shortcut names in the entire project.
    This is the single place where url names are written in python - elsewhere, they are accessed via this Enum.
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
    CLASSROOM_LIST_UPLOAD = "classroom_list"
    FILE_UPLOAD_PAGE = "file_upload_page"
    FIXED_CLASSES_UPLOAD = "fixed_classes"
    PUPIL_LIST_UPLOAD = "pupil_list"
    TEACHER_LIST_UPLOAD = "teacher_list"
    TIMETABLE_STRUCTURE_UPLOAD = "timetable_structure"
    UNSOLVED_CLASSES_UPLOAD = "unsolved_classes"

    # Create timetables app
    CREATE_TIMETABLES = "create_timetables"

    # View timetables app
    PUPILS_NAVIGATOR = "pupils_navigator"
    PUPIL_TIMETABLE = "pupil_timetable"  # Note reverse also requires a pupil id
    TEACHERS_NAVIGATOR = "teachers_navigator"
    TEACHER_TIMETABLE = "teacher_timetable"  # Note reverse also requires a teacher id
    VIEW_TIMETABLES_DASH = "selection_dashboard"
