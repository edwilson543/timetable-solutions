"""
Module defining constants relating to urls.
"""

# Standard library imports
from enum import StrEnum

# Django import
from django import urls


class UrlName(StrEnum):
    """
    Enumeration of ALL url shortcut names in the entire project.

    This is the single place where url names are written in python - elsewhere, they are accessed via this Enum, for
    example whenever urls.reverse is called, the argument is accessed from this Enum. Also in all apps' url dispatchers.
    Note however that some django html templates access the string versions via the {% url <url_name> %} tag, so these
    would need updating.
    """

    def url(self, lazy: bool = False, **kwargs: str | int | None) -> str:
        """
        Get the url of one of the enum members.
        raises: NoReverseMatch if incorrect kwargs supplied.
        """
        kwargs = kwargs or {}
        try:
            reverser = urls.reverse_lazy if lazy else urls.reverse
            return reverser(self, kwargs=kwargs)
        except urls.exceptions.NoReverseMatch:
            raise urls.exceptions.NoReverseMatch(
                f"Invalid kwargs: {kwargs}, for url alias: {self}"
            )

    # Users app
    DASHBOARD = "dashboard"
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_CHANGE_DONE = "password_change_done"
    PROFILE_REGISTRATION = "profile_registration"
    REGISTER = "register"
    REGISTER_PIVOT = "registration_pivot"
    SCHOOL_REGISTRATION = "school_registration"

    # --------------------
    # Data management
    # --------------------
    # Teachers
    TEACHER_LANDING_PAGE = "teacher-landing-page"
    TEACHER_LIST = "teacher-list"

    # Data upload app
    FILE_UPLOAD_PAGE = "file_upload_page"

    # File upload urls
    BREAKS_UPLOAD = "breaks_upload"
    CLASSROOM_LIST_UPLOAD = "classroom_upload"
    LESSONS_UPLOAD = "lessons_upload"
    PUPIL_LIST_UPLOAD = "pupil_upload"
    TEACHER_LIST_UPLOAD = "teacher_upload"
    TIMETABLE_STRUCTURE_UPLOAD = "timetable_upload"
    YEAR_GROUP_UPLOAD = "year_group_upload"

    # File upload reset urls
    ALL_DATA_RESET = "all_data_reset"
    BREAKS_RESET = "breaks_reset"
    CLASSROOM_LIST_RESET = "classroom_reset"
    LESSONS_RESET = "lessons_reset"
    PUPIL_LIST_RESET = "pupil_reset"
    TEACHER_LIST_RESET = "teacher_reset"
    TIMETABLE_STRUCTURE_RESET = "timetable_reset"
    YEAR_GROUP_RESET = "year_group_reset"

    # Example file download urls
    BREAKS_DOWNLOAD = "breaks_download"
    CLASSROOM_DOWNLOAD = "classroom_download"
    LESSONS_DOWNLOAD = "lessons_download"
    PUPIL_DOWNLOAD = "pupil_download"
    TEACHER_DOWNLOAD = "teacher_download"
    TIMETABLE_DOWNLOAD = "timetable_download"
    YEAR_GROUP_DOWNLOAD = "year_group_download"

    # Create timetables app
    CREATE_TIMETABLES = "create_timetables"

    # View timetables app
    PUPILS_NAVIGATOR = "pupils_navigator"
    PUPIL_TIMETABLE = "pupil_timetable"  # kwargs: pupil_id
    TEACHERS_NAVIGATOR = "teachers_navigator"
    TEACHER_TIMETABLE = "teacher_timetable"  # kwargs: teacher_id
    VIEW_TIMETABLES_DASH = "selection_dashboard"

    # Custom admin app
    CUSTOM_ADMIN_HOME = "user_admin:index"
    CUSTOM_ADMIN_TEACHER_LIST = "user_admin:data_teacher_changelist"
    CUSTOM_ADMIN_CLASSROOM_LIST = "user_admin:data_classroom_changelist"
    CUSTOM_ADMIN_YEAR_GROUP_LIST = "user_admin:data_yeargroup_changelist"
    CUSTOM_ADMIN_TIMETABLE_LIST = "user_admin:data_timetableslot_changelist"
    CUSTOM_ADMIN_PUPIL_LIST = "user_admin:data_pupil_changelist"
    CUSTOM_ADMIN_LESSON_LIST = "user_admin:data_lesson_changelist"
    CUSTOM_ADMIN_PROFILE = "user_admin:data_profile_changelist"

    # HTMX #

    # Users app
    DATA_UPLOAD_DASH_TAB = "data-upload-dash-tab"
    CREATE_TIMETABLE_DASH_TAB = "create-timetable-dash-tab"
    VIEW_TIMETABLE_DASH_TAB = "view-timetable-dash-tab"
    USERNAME_FIELD_REGISTRATION = "username-field-registration"

    # View timetables app
    LESSON_DETAIL = "lesson-detail"
    CLOSE_LESSON_DETAIL = "close-lesson-detail"
