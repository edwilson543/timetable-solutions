"""
Useful htmx view functionality.
"""

# Django imports
from django import http


class HTMXViewMixin:
    """
    Helpers for testing for htmx requests, like django-htmx.
    """

    request: http.HttpRequest

    @property
    def is_htmx(self) -> bool:
        return "HX-Request" in self.request.headers

    @property
    def is_htmx_get_request(self) -> bool:
        return self.request.method == "GET" and self.is_htmx

    @property
    def is_htmx_post_request(self) -> bool:
        return self.request.method == "POST" and self.is_htmx
