"""URLs module for view_timetables app."""

# Django imports
from django.urls import path

# Local application imports
from interfaces.constants import UrlName

from . import views

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
        views.lesson_detail_modal,
        name=UrlName.LESSON_DETAIL.value,
    ),
]
