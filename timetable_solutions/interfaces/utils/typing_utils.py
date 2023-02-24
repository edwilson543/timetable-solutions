"""
Utility types for use throughout interfaces layer.
"""

from typing import Protocol, TypeVar

from django import forms
from django import http
from django.contrib.auth import models as auth_models
from django_htmx.middleware import HtmxDetails

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
