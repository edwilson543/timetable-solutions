# Standard library imports
from typing import Any, ClassVar

# Django imports
from django import http
from django.contrib import messages
from django.contrib.auth import mixins
from django.views import generic

# Local application imports
from domain.data_management import upload_processors
from interfaces.constants import UrlName
from interfaces.data_management import forms
from interfaces.utils.typing_utils import AuthenticatedHttpRequest


class UploadView(mixins.LoginRequiredMixin, generic.FormView):
    """Page for uploading a file that populates one of the db tables."""

    # Defaults
    form_class = forms.BulkUpload

    # Class vars set per subclass
    upload_processor_class: ClassVar[type[upload_processors.Processor]]
    upload_url: ClassVar[str]
    example_download_url: ClassVar[str]

    # Instance vars
    school_id: int

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> None:
        super().setup(request, *args, **kwargs)
        self.school_id = request.user.profile.school.school_access_key

    def form_valid(self, form: forms.BulkUpload) -> http.HttpResponse:
        """Try to process the uploaded file into the db."""
        csv_file = form.cleaned_data["csv_file"]
        processor = self.upload_processor_class(
            school_access_key=self.school_id, csv_file=csv_file
        )
        if processor.upload_error_message:
            messages.error(request=self.request, message=processor.upload_error_message)
            return super().form_invalid(form=form)

        messages.success(
            request=self.request,
            message=f"Successfully saved your data for {processor.n_model_instances_created} "
            f"{self.upload_processor_class.model.Constant.human_string_plural}!",
        )
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add the relevant urls to the context."""
        context = super().get_context_data(**kwargs)
        context["upload_url"] = self.upload_url
        context["example_download_url"] = self.example_download_url
        return context
