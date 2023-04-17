"""
Module defining constants relating to urls.
"""

# Standard library imports
from enum import StrEnum

# Django imports
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
    PROFILE_REGISTRATION = "profile_registration"
    REGISTER = "register"
    REGISTER_PIVOT = "registration_pivot"
    SCHOOL_REGISTRATION = "school_registration"

    # --------------------
    # Data management
    # --------------------

    # Breaks
    BREAK_ADD_TEACHERS_PARTIAL = "break-add-teachers-partial"  # kwargs: break_id: str
    BREAK_CREATE = "break-create"
    BREAK_DOWNLOAD = "break-download"
    BREAK_LANDING_PAGE = "break-landing-page"
    BREAK_LIST = "break-list"
    BREAK_UPDATE = "break-update"  # kwargs: break_id: str
    BREAK_UPLOAD = "break-upload"

    # Classrooms
    CLASSROOM_CREATE = "classroom-create"
    CLASSROOM_DOWNLOAD = "classroom-download"
    CLASSROOM_LANDING_PAGE = "classroom-landing-page"
    CLASSROOM_LESSONS_PARTIAL = "classroom-lessons-partial"  # kwargs: classroom_id: int
    CLASSROOM_LIST = "classroom-list"
    CLASSROOM_UPDATE = "classroom-update"  # kwargs: classroom_id: int
    CLASSROOM_UPLOAD = "classroom-upload"

    # Pupils
    PUPIL_CREATE = "pupil-create"
    PUPIL_DOWNLOAD = "pupil-download"
    PUPIL_LANDING_PAGE = "pupil-landing-page"
    PUPIL_LESSONS_PARTIAL = "pupil-lessons-partial"  # kwargs: pupil_id: int
    PUPIL_LIST = "pupil-list"
    PUPIL_UPDATE = "pupil-update"  # kwargs: pupil_id: int
    PUPIL_UPLOAD = "pupil-upload"

    # Teachers
    TEACHER_CREATE = "teacher-create"
    TEACHER_DOWNLOAD = "teacher-download"
    TEACHER_LANDING_PAGE = "teacher-landing-page"
    TEACHER_LESSONS_PARTIAL = "teacher-lessons-partial"  # kwargs: teacher_id: int
    TEACHER_LIST = "teacher-list"
    TEACHER_UPDATE = "teacher-update"  # kwargs: teacher_id: int
    TEACHER_UPLOAD = "teacher-upload"

    # Timetable slot
    TIMETABLE_SLOT_CREATE = "timetable-slot-create"
    TIMETABLE_SLOT_DOWNLOAD = "timetable-slot-download"
    TIMETABLE_SLOT_LANDING_PAGE = "timetable-slot-landing-page"
    TIMETABLE_SLOT_LIST = "timetable-slot-list"
    TIMETABLE_SLOT_UPDATE = "timetable-slot-update"  # kwargs: slot_id: int
    TIMETABLE_SLOT_UPLOAD = "timetable-slot-upload"

    # Year groups
    YEAR_GROUP_CREATE = "year-group-create"
    YEAR_GROUP_DOWNLOAD = "year-group-download"
    YEAR_GROUP_LANDING_PAGE = "year-group-landing-page"
    YEAR_GROUP_LIST = "year-group-list"
    YEAR_GROUP_UPDATE = "year-group-update"  # kwargs: year_group_id: int
    YEAR_GROUP_UPLOAD = "year-group-upload"

    # Create timetables app
    CREATE_TIMETABLES = "create_timetables"

    # View timetables app
    PUPIL_TIMETABLE = "pupil_timetable"  # kwargs: pupil_id: int
    TEACHER_TIMETABLE = "teacher_timetable"  # kwargs: teacher_id: int
    LESSON_DETAIL = "lesson-detail"  # kwargs: lesson_id: str
