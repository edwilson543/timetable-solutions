"""
Utility types for use throughout interfaces layer.
"""

from typing import Protocol, TypeVar

from django import forms
from django import http
from django.contrib.auth import models as auth_models

from data import models


class _UserWithProfile(Protocol):
    """Helper to let type checkers know that users have profiles."""

    profile: models.Profile


class AuthenticatedHttpRequest(http.HttpRequest):
    """Type hint for a HTTP request from an authenticated user."""

    user: auth_models.User | _UserWithProfile


class HtmxHttpRequest(http.HttpRequest):
    """Type hint for a request submitted via a htmx ajax request."""

    pass


# Generic type hint for a form
FormSubclass = TypeVar("FormSubclass", bound=forms.Form)
