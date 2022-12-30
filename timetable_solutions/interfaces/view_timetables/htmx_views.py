"""
Views handling AJAX requests submitted via HTMX.
"""

# Django imports
from django import http
from django.template import loader
from django.contrib.auth.decorators import login_required

# Local application imports
from data import models
from interfaces.utils import typing_utils


@login_required
def lesson_detail_modal(
    request: typing_utils.HtmxHttpRequest, lesson_pk: int
) -> http.HttpResponse:
    """
    View populating a modal with the details for a specific Lesson instance.
    """
    template = loader.get_template("partials/lesson_detail.html")

    if request.method == "GET":
        lesson: models.Lesson = models.Lesson.get_lesson_by_pk(pk=lesson_pk)
        context = {
            "modal_is_active": True,
            "lesson": lesson,
            "lesson_title": lesson.lesson_id.replace("_", " ").title(),
        }
        return http.HttpResponse(template.render(context=context, request=request))


@login_required
def close_lesson_detail_modal(
    request: typing_utils.HtmxHttpRequest,
) -> http.HttpResponse:
    """
    View to close the less detail modal
    """
    template = loader.get_template("partials/lesson_detail.html")
    if request.method == "GET":
        context = {"modal_is_active": False}
        return http.HttpResponse(template.render(context=context, request=request))
