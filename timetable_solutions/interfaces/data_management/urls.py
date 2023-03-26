"""
Urls for data management views.
"""

# Django imports
from django.urls import path

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import views

urlpatterns = [
    # --------------------
    # Breaks
    # --------------------
    path(
        "breaks/",
        views.BreakLanding.as_view(),
        name=UrlName.BREAK_LANDING_PAGE.value,
    ),
    path(
        "breaks/create/",
        views.BreakCreate.as_view(),
        name=UrlName.BREAK_CREATE.value,
    ),
    path(
        "breaks/list/",
        views.BreakSearch.as_view(),
        name=UrlName.BREAK_LIST.value,
    ),
    path(
        "breaks/list/<str:break_id>/",
        views.BreakUpdate.as_view(),
        name=UrlName.BREAK_UPDATE.value,
    ),
    path(
        "breaks/list/<str:break_id>/teachers/",
        views.BreakAddRelatedTeachersPartial.as_view(),
        name=UrlName.BREAK_ADD_TEACHERS_PARTIAL.value,
    ),
    path(
        "breaks/upload/",
        views.BreakUpload.as_view(),
        name=UrlName.BREAK_UPLOAD.value,
    ),
    path(
        "breaks/download/",
        views.BreakExampleDownload.as_view(),
        name=UrlName.BREAK_DOWNLOAD.value,
    ),
    # --------------------
    # Classrooms
    # --------------------
    path(
        "classrooms/",
        views.ClassroomLanding.as_view(),
        name=UrlName.CLASSROOM_LANDING_PAGE.value,
    ),
    path(
        "classrooms/create/",
        views.ClassroomCreate.as_view(),
        name=UrlName.CLASSROOM_CREATE.value,
    ),
    path(
        "classrooms/list/",
        views.ClassroomSearch.as_view(),
        name=UrlName.CLASSROOM_LIST.value,
    ),
    path(
        "classrooms/list/<int:classroom_id>/",
        views.ClassroomUpdate.as_view(),
        name=UrlName.CLASSROOM_UPDATE.value,
    ),
    path(
        "classrooms/list/<int:classroom_id>/lessons/",
        views.ClassroomLessonsPartial.as_view(),
        name=UrlName.CLASSROOM_LESSONS_PARTIAL.value,
    ),
    path(
        "classrooms/upload/",
        views.ClassroomUpload.as_view(),
        name=UrlName.CLASSROOM_UPLOAD.value,
    ),
    path(
        "classrooms/download/",
        views.ClassroomExampleDownload.as_view(),
        name=UrlName.CLASSROOM_DOWNLOAD.value,
    ),
    # --------------------
    # Pupils
    # --------------------
    path(
        "pupils/",
        views.PupilLanding.as_view(),
        name=UrlName.PUPIL_LANDING_PAGE.value,
    ),
    path(
        "pupils/create/",
        views.PupilCreate.as_view(),
        name=UrlName.PUPIL_CREATE.value,
    ),
    path(
        "pupils/list/",
        views.PupilSearch.as_view(),
        name=UrlName.PUPIL_LIST.value,
    ),
    path(
        "pupils/list/<int:pupil_id>/",
        views.PupilUpdate.as_view(),
        name=UrlName.PUPIL_UPDATE.value,
    ),
    path(
        "pupils/list/<int:pupil_id>/lessons/",
        views.PupilLessonsPartial.as_view(),
        name=UrlName.PUPIL_LESSONS_PARTIAL.value,
    ),
    path(
        "pupils/upload/",
        views.PupilUpload.as_view(),
        name=UrlName.PUPIL_UPLOAD.value,
    ),
    path(
        "pupils/download/",
        views.PupilExampleDownload.as_view(),
        name=UrlName.PUPIL_DOWNLOAD.value,
    ),
    # --------------------
    # Teachers
    # --------------------
    path(
        "teachers/",
        views.TeacherLanding.as_view(),
        name=UrlName.TEACHER_LANDING_PAGE.value,
    ),
    path(
        "teachers/create/",
        views.TeacherCreate.as_view(),
        name=UrlName.TEACHER_CREATE.value,
    ),
    path(
        "teachers/list/",
        views.TeacherSearch.as_view(),
        name=UrlName.TEACHER_LIST.value,
    ),
    path(
        "teachers/list/<int:teacher_id>/",
        views.TeacherUpdate.as_view(),
        name=UrlName.TEACHER_UPDATE.value,
    ),
    path(
        "teachers/list/<int:teacher_id>/lessons/",
        views.TeacherLessonsPartial.as_view(),
        name=UrlName.TEACHER_LESSONS_PARTIAL.value,
    ),
    path(
        "teachers/upload/",
        views.TeacherUpload.as_view(),
        name=UrlName.TEACHER_UPLOAD.value,
    ),
    path(
        "teachers/download/",
        views.TeacherExampleDownload.as_view(),
        name=UrlName.TEACHER_DOWNLOAD.value,
    ),
    # --------------------
    # Timetable slots
    # --------------------
    path(
        "timetable-slots/",
        views.TimetableSlotLanding.as_view(),
        name=UrlName.TIMETABLE_SLOT_LANDING_PAGE.value,
    ),
    path(
        "timetable-slots/create/",
        views.TimetableSlotCreate.as_view(),
        name=UrlName.TIMETABLE_SLOT_CREATE.value,
    ),
    path(
        "timetable-slots/list/",
        views.TimetableSlotSearch.as_view(),
        name=UrlName.TIMETABLE_SLOT_LIST.value,
    ),
    path(
        "timetable-slots/list/<int:slot_id>/",
        views.TimetableSlotUpdate.as_view(),
        name=UrlName.TIMETABLE_SLOT_UPDATE.value,
    ),
    path(
        "timetable-slots/upload/",
        views.TimetableSlotUpload.as_view(),
        name=UrlName.TIMETABLE_SLOT_UPLOAD.value,
    ),
    path(
        "timetable-slots/download/",
        views.TimetableSlotExampleDownload.as_view(),
        name=UrlName.TIMETABLE_SLOT_DOWNLOAD.value,
    ),
    # --------------------
    # Year groups
    # --------------------
    path(
        "yeargroups/",
        views.YearGroupLanding.as_view(),
        name=UrlName.YEAR_GROUP_LANDING_PAGE.value,
    ),
    path(
        "yeargroups/create/",
        views.YearGroupCreate.as_view(),
        name=UrlName.YEAR_GROUP_CREATE.value,
    ),
    path(
        "yeargroups/list/",
        views.YearGroupList.as_view(),
        name=UrlName.YEAR_GROUP_LIST.value,
    ),
    path(
        "yeargroups/list/<int:year_group_id>/",
        views.YearGroupUpdate.as_view(),
        name=UrlName.YEAR_GROUP_UPDATE.value,
    ),
    path(
        "yeargroups/upload/",
        views.YearGroupUpload.as_view(),
        name=UrlName.YEAR_GROUP_UPLOAD.value,
    ),
    path(
        "yeargroups/download/",
        views.YearGroupExampleDownload.as_view(),
        name=UrlName.YEAR_GROUP_DOWNLOAD.value,
    ),
]
