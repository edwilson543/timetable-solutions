"""Urls module for the data_upload app"""

# Django imports
from django.urls import path

# Local application imports
from domain.data_upload_processing.constants import ExampleFile
from constants.url_names import UrlName
from . import views

urlpatterns = [
    # BASE data upload page
    path("", views.UploadPage.as_view(), name=UrlName.FILE_UPLOAD_PAGE.value),
    # Data UPLOAD endpoints
    path(
        "pupil_upload/",
        views.PupilListUpload.as_view(),
        name=UrlName.PUPIL_LIST_UPLOAD.value,
    ),
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
        "timetable_upload/",
        views.TimetableStructureUpload.as_view(),
        name=UrlName.TIMETABLE_STRUCTURE_UPLOAD.value,
    ),
    path(
        "lesson_upload/",
        views.LessonsUpload.as_view(),
        name=UrlName.LESSONS_UPLOAD.value,
    ),
    # Data RESET endpoints
    path(
        "pupil_reset/",
        views.PupilListReset.as_view(),
        name=UrlName.PUPIL_LIST_RESET.value,
    ),
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
        "timetable_reset/",
        views.TimetableStructureReset.as_view(),
        name=UrlName.TIMETABLE_STRUCTURE_RESET.value,
    ),
    path(
        "lesson_reset/", views.LessonReset.as_view(), name=UrlName.LESSONS_RESET.value
    ),
    path(
        "all_data_reset/",
        views.AllSchoolDataReset.as_view(),
        name=UrlName.ALL_DATA_RESET.value,
    ),
    # Data example DOWNLOAD endpoints
    path(
        "pupil_download/",
        views.PupilDownload.as_view(),
        name=UrlName.PUPIL_DOWNLOAD.value,
    ),
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
        "timetable_download/",
        views.TimetableDownload.as_view(),
        name=UrlName.TIMETABLE_DOWNLOAD.value,
    ),
    path(
        "lesson_download/",
        views.LessonDownload.as_view(),
        name=UrlName.LESSONS_DOWNLOAD.value,
    ),
]
