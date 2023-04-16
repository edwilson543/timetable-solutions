"""
Views used to navigate users towards an individual pupil/teacher's timetable.
"""

# Django imports
from django import http, shortcuts
from django.contrib.auth.decorators import login_required
from django.template import loader

# Local application imports
from data import models
from domain import view_timetables
from interfaces.utils import typing_utils


@login_required
def pupil_timetable(request: http.HttpRequest, pupil_id: int) -> http.HttpResponse:
    """
    View for rendering the timetable of the individual pupil with the passed id.
    Note that the pupil_id is unique together with the school access key,
    and so different users will see different content at the requested url.
    """
    school_id = request.user.profile.school.school_access_key
    pupil = models.Pupil.objects.get_individual_pupil(
        school_id=school_id, pupil_id=pupil_id
    )
    timetable = view_timetables.get_pupil_timetable(pupil)

    template = loader.get_template("view_timetables/pupil-timetable.html")
    context = {
        "pupil": pupil,
        "timetable": timetable,
    }
    return http.HttpResponse(template.render(context, request))


@login_required
def teacher_timetable(request: http.HttpRequest, teacher_id: int) -> http.HttpResponse:
    """
    View for the timetable of the individual teacher with the passed id.
    Note that the teacher_id is unique together with the school access key,
    and so different users will see different content at the requested url.
    """
    school_id = request.user.profile.school.school_access_key
    teacher = models.Teacher.objects.get_individual_teacher(
        school_id=school_id, teacher_id=teacher_id
    )
    timetable = view_timetables.get_teacher_timetable(teacher)

    template = loader.get_template("view_timetables/teacher-timetable.html")
    context = {
        "teacher": teacher,
        "timetable": timetable,
    }
    return http.HttpResponse(template.render(context, request))


@login_required
def lesson_detail_modal(
    request: typing_utils.AuthenticatedHtmxRequest, lesson_id: str
) -> http.HttpResponse:
    """
    Populate a modal with the details for a specific Lesson.

    Note the modal can only be populated by a hx-get request.
    """
    template_name = "partials/lesson-detail.html"

    if request.htmx and request.method == "GET":
        school_id = request.user.profile.school.school_access_key
        lesson = models.Lesson.objects.get_individual_lesson(
            school_id=school_id, lesson_id=lesson_id
        )
        context = {
            "modal_is_active": True,
            "lesson": lesson,
            "lesson_title": lesson.lesson_id.replace("_", " ").title(),
            "close_modal_url": request.htmx.current_url_abs_path,
        }
        return shortcuts.render(
            template_name=template_name, context=context, request=request
        )
