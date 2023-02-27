# Standard library imports
from pathlib import Path
from typing import ClassVar

# Django imports
from django import http
from django.contrib.auth import mixins
from django.views import generic

# Local application imports
from interfaces.utils.typing_utils import AuthenticatedHttpRequest


class ExampleDownloadBase(mixins.LoginRequiredMixin, generic.View):
    """Class responsible for allowing users to download the example files."""

    # Default django vars
    http_method_names = ["get"]

    # Custom class vars
    example_filepath: ClassVar[Path]
    """The location on the filesystem of the file users will be given as an example."""

    def get(self, request: AuthenticatedHttpRequest) -> http.FileResponse:
        """Attach the relevant example file in the response."""
        response = http.FileResponse(
            open(self.example_filepath, "rb"), as_attachment=True
        )
        return response
