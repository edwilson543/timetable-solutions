# Standard library imports
from pathlib import Path

# Django imports
from django import http
from django.contrib.auth import mixins
from django.views import generic

# Local application imports
from interfaces.utils.typing_utils import AuthenticatedHttpRequest


class ExampleDownloadBase(mixins.LoginRequiredMixin, generic.View):
    """Class responsible for allowing users to download the example files."""

    http_method_names = ["get"]

    example_filepath: Path

    def get(self, request: AuthenticatedHttpRequest) -> http.FileResponse:
        """Attach the relevant example file in the response."""
        response = http.FileResponse(
            open(self.example_filepath, "rb"), as_attachment=True
        )
        return response
