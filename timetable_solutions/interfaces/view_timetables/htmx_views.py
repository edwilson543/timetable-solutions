"""
Views handling AJAX requests submitted via HTMX.
"""

# Django imports
from django import http
from django.template import loader
from django.contrib.auth.decorators import login_required

# Local application imports
from data import models


@login_required
def lesson_detail_modal(request: http.HttpRequest, lesson_pk: int) -> http.HttpResponse:
    """
    View populating a modal with the details for a specific Lesson instance.
    """
    template = loader.get_template("partials/lesson_detail.html")

    if request.method == "GET":
        lesson = models.Lesson.objects.get(pk=lesson_pk)
        context = {
            "modal_is_active": True,
            "lesson": lesson
        }
        return template.render(context=context, request=request)

    if request.method == "DELETE":
        context = {"modal_is_active": False}
        return template.render(context=context, request=request)