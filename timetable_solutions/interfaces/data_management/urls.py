"""Urls module for the data_upload app"""

# Django imports
from django.urls import path

# Local application imports
from interfaces.constants import UrlName
from . import views

urlpatterns = [
    # BASE data upload page
    path("", views.UploadPage.as_view(), name=UrlName.FILE_UPLOAD_PAGE.value),
    # --------------------
    # Teachers
    # --------------------
    path(
        "teachers/",
        views.TeacherLanding.as_view(),
        name=UrlName.TEACHERS_LANDING_PAGE.value,
    ),
    # --------------------
    # Data UPLOAD endpoints
    # --------------------
    path(
        "teacher_upload/",
        views.TeacherListUpload.as_view(),
        name=UrlName.TEACHER_LIST_UPLOAD.value,
    ),
    path(
        "classroom_upload/",
        views.ClassroomListUpload.as_view(),
        name=UrlName.CLASSROOM_LIST_UPLOAD.value,
    ),
    path(
        "year_group_upload/",
        views.YearGroupListUpload.as_view(),
        name=UrlName.YEAR_GROUP_UPLOAD.value,
    ),
    path(
        "pupil_upload/",
        views.PupilListUpload.as_view(),
        name=UrlName.PUPIL_LIST_UPLOAD.value,
    ),
    path(
        "timetable_upload/",
        views.TimetableStructureUpload.as_view(),
        name=UrlName.TIMETABLE_STRUCTURE_UPLOAD.value,
    ),
    path(
        "lesson_upload/",
        views.LessonsUpload.as_view(),
        name=UrlName.LESSONS_UPLOAD.value,
    ),
    path(
        "break_upload/", views.BreaksUpload.as_view(), name=UrlName.BREAKS_UPLOAD.value
    ),
    # --------------------
    # Data RESET endpoints
    # --------------------
    path(
        "teacher_reset/",
        views.TeacherListReset.as_view(),
        name=UrlName.TEACHER_LIST_RESET.value,
    ),
    path(
        "classroom_reset/",
        views.ClassroomListReset.as_view(),
        name=UrlName.CLASSROOM_LIST_RESET.value,
    ),
    path(
        "year_group_reset/",
        views.YearGroupReset.as_view(),
        name=UrlName.YEAR_GROUP_RESET.value,
    ),
    path(
        "pupil_reset/",
        views.PupilListReset.as_view(),
        name=UrlName.PUPIL_LIST_RESET.value,
    ),
    path(
        "timetable_reset/",
        views.TimetableStructureReset.as_view(),
        name=UrlName.TIMETABLE_STRUCTURE_RESET.value,
    ),
    path(
        "lesson_reset/",
        views.LessonReset.as_view(),
        name=UrlName.LESSONS_RESET.value,
    ),
    path(
        "break_reset/",
        views.BreakReset.as_view(),
        name=UrlName.BREAKS_RESET.value,
    ),
    path(
        "all_data_reset/",
        views.AllSchoolDataReset.as_view(),
        name=UrlName.ALL_DATA_RESET.value,
    ),
    # --------------------
    # Data example DOWNLOAD endpoints
    # --------------------
    path(
        "teacher_download/",
        views.TeacherDownload.as_view(),
        name=UrlName.TEACHER_DOWNLOAD.value,
    ),
    path(
        "classroom_download/",
        views.ClassroomDownload.as_view(),
        name=UrlName.CLASSROOM_DOWNLOAD.value,
    ),
    path(
        "year_group_download/",
        views.YearGroupDownload.as_view(),
        name=UrlName.YEAR_GROUP_DOWNLOAD.value,
    ),
    path(
        "pupil_download/",
        views.PupilDownload.as_view(),
        name=UrlName.PUPIL_DOWNLOAD.value,
    ),
    path(
        "timetable_download/",
        views.TimetableDownload.as_view(),
        name=UrlName.TIMETABLE_DOWNLOAD.value,
    ),
    path(
        "lesson_download/",
        views.LessonDownload.as_view(),
        name=UrlName.LESSONS_DOWNLOAD.value,
    ),
    path(
        "break_download",
        views.BreakDownload.as_view(),
        name=UrlName.BREAKS_DOWNLOAD.value,
    ),
]
