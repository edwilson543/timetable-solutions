"""
Utility types for use throughout interfaces layer.
"""

# Standard library imports
from typing import Protocol, TypeVar

# Third party imports
from django_htmx.middleware import HtmxDetails

# Django imports
from django import forms, http
from django.contrib.auth import models as auth_models

# Local application imports
from data import models


class _UserWithProfile(Protocol):
    """Helper to let type checkers know that users have profiles."""

    profile: models.Profile


class AuthenticatedHttpRequest(http.HttpRequest):
    """Type hint for an HTTP request from an authenticated user."""

    user: auth_models.User | _UserWithProfile


class AuthenticatedHtmxRequest(AuthenticatedHttpRequest):
    """Type hint for a request submitted via an htmx ajax request."""

    htmx: HtmxDetails


# Generic type hint for a form
FormSubclass = TypeVar("FormSubclass", bound=forms.Form)
