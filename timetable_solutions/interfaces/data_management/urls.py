"""Urls for data management views."""

# Django imports
from django.urls import path

# Local application imports
from interfaces.constants import UrlName

from . import views

urlpatterns = [
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
        "teachers/upload/",
        views.TeacherUpload.as_view(),
        name=UrlName.TEACHER_UPLOAD.value,
    ),
    path(
        "teachers/download/",
        views.TeacherExampleDownload.as_view(),
        name="teacher-download",
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
        name="year-group-download",
    ),
]
