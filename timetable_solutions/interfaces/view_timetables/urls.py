"""URLs module for view_timetables app."""

# Django imports
from django.urls import path

# Local application imports
from interfaces.constants import UrlName

from . import htmx_views, views

urlpatterns = [
    # View timetable URLs
    path(
        "pupils/<int:pupil_id>",
        views.pupil_timetable,
        name=UrlName.PUPIL_TIMETABLE.value,
    ),
    path(
        "teachers/<int:teacher_id>",
        views.teacher_timetable,
        name=UrlName.TEACHER_TIMETABLE.value,
    ),
    # HTMX URLs
    path(
        "lesson-detail-modal/<str:lesson_id>",
        htmx_views.lesson_detail_modal,
        name=UrlName.LESSON_DETAIL.value,
    ),
    path(
        "close-lesson-detail-modal/",
        htmx_views.close_lesson_detail_modal,
        name=UrlName.CLOSE_LESSON_DETAIL.value,
    ),
]
