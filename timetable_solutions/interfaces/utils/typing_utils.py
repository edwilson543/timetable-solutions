"""
Utility types for use throughout interfaces layer.
"""

# Standard library imports
from typing import TypeVar

# Django imports
from django import forms
from django import http


# Type hint for a request submitted via a htmx ajax request
class HtmxHttpRequest(http.HttpRequest):
    pass


# Generic type hint for a form
FormSubclass = TypeVar("FormSubclass", bound=forms.Form)
