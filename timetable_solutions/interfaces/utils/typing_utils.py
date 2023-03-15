"""
Utility types for use throughout interfaces layer.
"""

# Standard library imports
from typing import TypeVar

# Third party imports
from django_htmx.middleware import HtmxDetails

# Django imports
from django import forms, http
from django.contrib.auth import models as auth_models


class AuthenticatedHttpRequest(http.HttpRequest):
    """Type hint for an HTTP request from an authenticated user."""

    user: auth_models.User


class AuthenticatedHtmxRequest(AuthenticatedHttpRequest):
    """Type hint for a request submitted via an htmx ajax request."""

    htmx: HtmxDetails


# Generic type hint for a form
FormSubclass = TypeVar("FormSubclass", bound=forms.Form)
