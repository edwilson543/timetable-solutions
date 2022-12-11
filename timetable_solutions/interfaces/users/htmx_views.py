"""
Views handling requests submitted by HTTP
"""

# Standard library imports
import enum

# Django imports
from django import http
from django import shortcuts
from django.contrib.auth import validators, models as auth_models
from django.core import exceptions


class FieldStatus(enum.StrEnum):
    """
    Enumeration of the icons displayed to users for inline field validation.
    """
    VALID = "✅"
    INVALID = "🚫"
    EMPTY = ""


def username_field_view(request: http.HttpRequest) -> http.HttpResponse:
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
                username_exists = auth_models.User.objects.filter(username=username).exists()
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
