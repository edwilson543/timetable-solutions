"""
Registration views handling requests submitted by HTMX.
"""

# Standard library imports
import enum

# Django imports
from django import http, shortcuts
from django.contrib.auth import models as auth_models
from django.contrib.auth import validators
from django.core import exceptions

# Local application imports
from interfaces.utils import typing_utils


class FieldStatus(enum.StrEnum):
    """
    Enumeration of the icons displayed to users for inline field validation.
    """

    VALID = "✅"
    INVALID = "🚫"
    EMPTY = ""


def username_field_view(
    request: typing_utils.AuthenticatedHtmxRequest,
) -> http.HttpResponse:
    """
    View providing inline validation for the username field.
    The template rendered is just the div wrapping the username field.
    """

    if request.method == "POST":
        username = request.POST.get("username")

        if username != "":
            # Starting assumptions
            username_valid = True
            username_exists = False

            try:
                validators.ASCIIUsernameValidator()(username)
                username_exists = auth_models.User.objects.filter(
                    username=username
                ).exists()
            except exceptions.ValidationError:
                username_valid = False

            if username_valid and not username_exists:
                context = {"USERNAME_VALID": FieldStatus.VALID.value}
            else:
                context = {"USERNAME_VALID": FieldStatus.INVALID.value}

        else:
            context = {"USERNAME_VALID": FieldStatus.EMPTY.value}

        partial = "partials/username_field.html"

        return shortcuts.render(request=request, template_name=partial, context=context)
