"""
Module defining constants relating to urls.
"""

# Standard library imports
from enum import StrEnum


class UrlName(StrEnum):
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
    ALL_DATA_RESET = "all_data_reset"

    # Example file download urls
    CLASSROOM_DOWNLOAD = "classroom_download"
    FIXED_CLASSES_DOWNLOAD = "fixed_class_download"
    PUPIL_DOWNLOAD = "pupil_download"
    TEACHER_DOWNLOAD = "teacher_download"
    TIMETABLE_DOWNLOAD = "timetable_download"
    UNSOLVED_CLASSES_DOWNLOAD = "unsolved_class_download"

    # Create timetables app
    CREATE_TIMETABLES = "create_timetables"

    # View timetables app
    PUPILS_NAVIGATOR = "pupils_navigator"
    PUPIL_TIMETABLE = "pupil_timetable"  # |---------->
    PUPIL_TT_CSV_DOWNLOAD = "pupil_tt_csv"  # Note reverse also requires a pupil id
    PUPIL_TT_PDF_DOWNLOAD = "pupil_tt_pdf"  # <----------|
    TEACHERS_NAVIGATOR = "teachers_navigator"
    TEACHER_TIMETABLE = "teacher_timetable"  # |---------->
    TEACHER_TT_CSV_DOWNLOAD = "teacher_tt_csv"  # Note reverse also requires a teacher id
    TEACHER_TT_PDF_DOWNLOAD = "teacher_tt_pdf"  # <----------|
    VIEW_TIMETABLES_DASH = "selection_dashboard"

    # Custom admin app
    CUSTOM_ADMIN_HOME = "user_admin:index"
