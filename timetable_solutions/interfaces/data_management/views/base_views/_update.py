# Standard library imports
import abc
from collections import OrderedDict
from typing import Any, ClassVar, Generic, TypeVar

# Third party imports
from rest_framework import serializers

# Django imports
from django import http
from django.contrib import messages
from django.contrib.auth import mixins
from django.db import models as django_models
from django.template import loader
from django.views import generic

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management.forms import base_forms
from interfaces.utils.typing_utils import (
    AuthenticatedHtmxRequest,
    AuthenticatedHttpRequest,
)

# Form submit buttons names
_UPDATE_SUBMIT = "update-submit"
_DELETE_SUBMIT = "delete-submit"


_ModelT = TypeVar("_ModelT", bound=django_models.Model)


class UpdateView(mixins.LoginRequiredMixin, generic.FormView, Generic[_ModelT]):
    """
    Page displaying a school's data for a single instance of a model,
    and allowing this data to be updated or deleted.
    """

    # Class vars
    model_class: type[_ModelT]
    """The model we are updating an instance of."""

    form_class: type[base_forms.CreateUpdate]
    """Form used to update a model instance (overridden from django's FormView)"""

    serializer_class: type[serializers.Serializer[_ModelT]]

    object_id_name: ClassVar[str]
    """Name of the object's id field, that is unique to the school. e.g. 'teacher_id', 'pupil_id'."""

    model_attributes_for_form_initials: ClassVar[list[str]]
    """The model attributes that should be set as the 'initial' values in the instantiated form."""

    page_url_prefix: ClassVar[UrlName]
    """
    Prefix of this page's url - where the search form should be submitted.
    The full url is constructed as page_url_prefix/<model_instance_id>.
    """

    delete_success_url: ClassVar[str]
    """URL to redirect to following a successful deletion."""

    enabled_form_template_name = "partials/forms/basic-form.html"
    """
    Location of the form partial to allow users to update object details.
    Note this is not included on initial page load, and is only rendered following
    a htmx get request sent from an "Edit" button.
    """

    # Instance vars
    school_id: int
    """The school who's data will be shown."""

    model_instance: _ModelT
    """The model who's data is rendered on this page."""

    model_instance_id: int | str
    """Id of the model instance, within the context of the school."""

    @abc.abstractmethod
    def update_model_from_clean_form(
        self, form: base_forms.CreateUpdate
    ) -> _ModelT | None:
        """
        Method used to try to update the target model instance from a clean form.

        Should handle any exceptions, and return None if an instance could not be created.
        """
        raise NotImplemented

    @abc.abstractmethod
    def delete_model_instance(self) -> http.HttpResponse:
        """
        Method used to delete the targeted model instance, as if handling HTTP delete requests.
        """
        raise NotImplemented

    # --------------------
    # Implementation of django hooks
    # --------------------
    def get(
        self, request: AuthenticatedHtmxRequest, *args: object, **kwargs: object
    ) -> http.HttpResponse:
        """
        Override get to handle a htmx request as well as the ordinary page load.

        The ordinary page load presents a disabled form only rendering the object details,
        which is made editable via a htmx get request.
        """
        if self.is_htmx_get_request:
            return self._get_htmx_response()
        else:
            return super().get(request=request, *args, **kwargs)

    def post(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> http.HttpResponse:
        """Pivot to either updating or deleting the data."""
        if self.is_delete_request:
            return self.delete_model_instance()
        elif self.is_update_request:
            return super().post(request, *args, **kwargs)

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: Any
    ) -> None:
        """Set some instance attributes used in later logic."""
        super().setup(request, *args, **kwargs)
        self.school_id = request.user.profile.school.school_access_key

        self.model_instance_id = kwargs[self.object_id_name]
        self.model_instance = self._get_object_or_404(self.model_instance_id)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add some additional context for the template."""
        context = super().get_context_data(**kwargs)
        context["serialized_model_instance"] = self._get_serialized_model_instance()
        context["page_url"] = self.page_url
        return context

    # --------------------
    # Handle the update form
    # --------------------
    def form_valid(self, form: base_forms.CreateUpdate) -> http.HttpResponse:
        """Use the form to update the relevant data."""
        if new_instance := self.update_model_from_clean_form(form=form):
            msg = f"Details for {new_instance} were successfully updated!"
            messages.success(request=self.request, message=msg)
            return http.HttpResponseRedirect(self.get_success_url())
        else:
            msg = f"Could not update details for {self.model_instance}."
            messages.error(request=self.request, message=msg)

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the model instance to the form kwargs so the values can be set as initials."""
        kwargs = super().get_form_kwargs()
        kwargs["school_id"] = self.school_id
        kwargs["initial"] = self._get_initial_form_kwargs()
        if self.is_delete_request:
            # Do not bind any data or files to this form
            kwargs.pop("data")
            kwargs.pop("files")
        return kwargs

    def get_success_url(self) -> str:
        """Redirect a posted form back to the same page."""
        return self.page_url

    # --------------------
    # Helper methods
    # --------------------

    def _get_htmx_response(self) -> http.HttpResponse:
        """Get an editable update form partial."""
        template = loader.get_template(template_name=self.enabled_form_template_name)
        context = {
            "form": self.get_form(),
            "form_id": "update-form",
            "submit_url": self.page_url,
            "submit_name": _UPDATE_SUBMIT,
            "submit_text": "Update",
            "other_button_url": self.page_url,
            "other_button_text": "Revert",
        }
        return http.HttpResponse(template.render(context=context, request=self.request))

    def _get_object_or_404(self, model_instance_id: int | str) -> _ModelT:
        """Retrieve the model instance we are updating."""
        try:
            return self.model_class.objects.get(
                school_id=self.school_id, **{self.object_id_name: model_instance_id}
            )
        except self.model_class.DoesNotExist:
            raise http.Http404

    def _get_serialized_model_instance(self) -> OrderedDict:
        """Serialize the model instance before passing as context."""
        return self.serializer_class(instance=self.model_instance).data

    def _get_initial_form_kwargs(self) -> dict[str, Any]:
        """Get the kwargs to pass to the form as the initial kwarg values."""
        return {
            attr: getattr(self.model_instance, attr)
            for attr in self.model_attributes_for_form_initials
        }

    # --------------------
    # Properties
    # --------------------
    @property
    def is_update_request(self) -> bool:
        """Whether this view is handling the attempted update of data."""
        return _UPDATE_SUBMIT in self.request.POST

    @property
    def is_delete_request(self) -> bool:
        """Whether this view is handling the attempted deletion of data."""
        return _DELETE_SUBMIT in self.request.POST

    @property
    def is_htmx_get_request(self) -> bool:
        """Whether the request being handled is an htmx request."""
        return (self.request.method == "GET") and (
            "Http-Hx-Request" in self.request.headers.keys() or bool(self.request.htmx)
        )

    @property
    def page_url(self) -> str:
        """Construct the full page url."""
        return self.page_url_prefix.url(
            lazy=False, **{self.object_id_name: self.model_instance_id}
        )
