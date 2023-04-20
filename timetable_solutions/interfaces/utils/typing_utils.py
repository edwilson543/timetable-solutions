"""
Utility types for use throughout interfaces layer.
"""

# Third party imports
from django_htmx.middleware import HtmxDetails

# Django imports
from django import http
from django.contrib.auth import models as auth_models

# Local application imports
from data import models


class RegisteredUser(auth_models.User):
    """A user who has completed registration and therefore has a profile."""

    profile: models.Profile

    class Meta:
        # Ensure django doesn't think this is some new model
        abstract = True


class AuthenticatedHttpRequest(http.HttpRequest):
    """Type hint for an HTTP request from an authenticated user."""

    user: RegisteredUser


class AuthenticatedHtmxRequest(AuthenticatedHttpRequest):
    """Type hint for a request submitted via an htmx ajax request."""

    htmx: HtmxDetails
