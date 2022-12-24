"""
Utility types for use throughout interfaces layer.
"""

# Django imports
from django import http


class HtmxHttpRequest(http.HttpRequest):
    pass
