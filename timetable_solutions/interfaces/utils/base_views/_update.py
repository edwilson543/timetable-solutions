# Standard library imports
import abc
from collections import OrderedDict
from typing import Any, ClassVar, Generic, TypeVar

# Third party imports
from rest_framework import serializers

# Django imports
from django import forms as django_forms
from django import http
from django.contrib import messages
from django.contrib.auth import mixins
from django.db import models as django_models
from django.template import loader
from django.views import generic

# Local application imports
from domain import base_exceptions
from interfaces.constants import UrlName
from interfaces.utils.base_views import _htmx_views
from interfaces.utils.typing_utils import (
    AuthenticatedHtmxRequest,
    AuthenticatedHttpRequest,
)

# Form submit buttons names
_UPDATE_SUBMIT = "update-submit"
_DELETE_SUBMIT = "delete-submit"


_ModelT = TypeVar("_ModelT", bound=django_models.Model)
_UpdateFormT = TypeVar("_UpdateFormT", bound=django_forms.Form)


class UpdateView(
    _htmx_views.HTMXViewMixin,
    mixins.LoginRequiredMixin,
    generic.FormView,
    Generic[_ModelT, _UpdateFormT],
):
    """
    Page displaying a school's data for a single instance of a model,
    and allowing this data to be updated or deleted.
    """

    # Class vars
    model_class: type[_ModelT]
    """The model we are updating an instance of."""

    form_class: type[_UpdateFormT]
    """Form used to update a model instance (overridden from django's FormView)"""

    serializer_class: type[serializers.Serializer[_ModelT]]
    """Serializer used to convert the model instance into JSON-like data."""

    prefetch_related: list[django_models.Prefetch] | None = None
    """Any relationships to prefetch when retrieving the model instance."""

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

    enabled_form_template_name = "utils/forms/basic-form.html"
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
    def update_model_from_clean_form(self, form: _UpdateFormT) -> _ModelT:
        """
        Method used to try to update the target model instance from a clean form.

        Should handle any exceptions, and return None if an instance could not be created.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_model_instance(self) -> None:
        """
        Method used to delete the targeted model instance, as if handling HTTP delete requests.
        """
        raise NotImplementedError

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
            return self._handle_deletion()
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
        context["submit_icon"] = "fa-solid fa-wrench"
        context["other_button_icon"] = "fa-solid fa-arrow-rotate-left"
        return context

    # --------------------
    # Handle the update form
    # --------------------

    def form_valid(self, form: _UpdateFormT) -> http.HttpResponse:
        """Use the form to update the relevant data."""
        try:
            new_instance = self.update_model_from_clean_form(form=form)
        except base_exceptions.UnableToUpdateModelInstance as exc:
            form.add_error(None, error=exc.human_error_message)
            return super().form_invalid(form=form)

        msg = f"Details for {new_instance} were successfully updated!"
        messages.success(request=self.request, message=msg)
        return http.HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the model instance to the form kwargs so the values can be set as initials."""
        kwargs = super().get_form_kwargs()
        kwargs["school_id"] = self.school_id
        kwargs["initial"] = self._get_initial_form_kwargs()
        if not self.is_update_request:
            # Do not bind any data or files to this form
            kwargs.pop("data", None)
            kwargs.pop("files", None)
        return kwargs

    def get_success_url(self) -> str:
        """Redirect a posted form back to the same page."""
        return self.page_url

    # --------------------
    # Handle the delete form
    # --------------------

    def _handle_deletion(self) -> http.HttpResponse:
        """
        Delete the model instance and handle any exceptions.
        """
        try:
            msg = f"{self.model_instance} was deleted."
            self.delete_model_instance()
            messages.success(request=self.request, message=msg)
        except base_exceptions.UnableToDeleteModelInstance as exc:
            context = self.get_context_data()
            context["deletion_error_message"] = exc.human_error_message
            return super().render_to_response(context=context)
        return http.HttpResponseRedirect(self.delete_success_url)

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
            "submit_icon": "fa-solid fa-wrench",
            "other_button_url": self.page_url,
            "other_button_text": "Revert",
            "other_button_icon": "fa-solid fa-arrow-rotate-left",
        }
        return http.HttpResponse(template.render(context=context, request=self.request))

    def _get_object_or_404(self, model_instance_id: int | str) -> _ModelT:
        """Retrieve the model instance we are updating."""
        try:
            if self.prefetch_related:
                objects = self.model_class.objects.prefetch_related(
                    *self.prefetch_related
                )
            else:
                objects = self.model_class.objects
            return objects.get(
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
    def page_url(self) -> str:
        """Construct the full page url."""
        return self.page_url_prefix.url(
            lazy=False, **{self.object_id_name: self.model_instance_id}
        )
