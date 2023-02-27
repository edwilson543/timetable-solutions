# Standard library imports
import abc
from typing import Any, ClassVar, Generic, TypeVar

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

_ModelT = TypeVar("_ModelT", bound=django_models.Model)


class UpdateView(mixins.LoginRequiredMixin, generic.FormView, Generic[_ModelT]):
    """
    Page displaying a school's data for a single instance of a model,
    and allowing this data to be updated.
    """

    # Class vars
    model_class: type[_ModelT]
    """The model we are updating an instance of."""

    form_class: type[base_forms.CreateUpdate]
    """Form used to update a model instance (overridden from django's FormView)"""

    deletion_form_class: type[base_forms.Delete]
    """Form used to delete the model instance."""

    object_id_name: ClassVar[str]
    """Name of the object's id field, that is unique to the school. e.g. 'teacher_id', 'pupil_id'."""

    model_attributes_for_form_initials: ClassVar[list[str]]
    """The model attributes that should be set as the 'initial' values in the instantiated form."""

    page_url_prefix: ClassVar[UrlName]
    """
    Prefix of this page's url - where the search form should be submitted.
    The full url is constructed as page_url_prefix/<model_instance_id>.
    """

    delete_url_prefix: ClassVar[UrlName]
    """URL prefix of the page to post to, to delete the model instance."""

    enabled_form_template_name = "data_management/partials/forms/update-form.html"
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
    def deletion_form_is_disabled(self) -> bool:
        """Whether the deletion form should be rendered as disabled (to prevent deletion)..."""
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
        if self.request_is_from_htmx:
            return self._get_htmx_response()
        else:
            return super().get(request=request, *args, **kwargs)

    def form_valid(self, form: base_forms.CreateUpdate) -> http.HttpResponse:
        """Use the form to update the relevant data."""
        if form.is_valid():
            if new_instance := self.update_model_from_clean_form(form=form):
                msg = f"Details for {new_instance} were successfully updated!"
                messages.success(request=self.request, message=msg)
                return super().form_valid(form=form)
            else:
                msg = f"Could not update details for {self.model_instance}."
                messages.error(request=self.request, message=msg)
                return super().form_invalid(form=form)
        else:
            return self.form_invalid(form=form)

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: Any
    ) -> None:
        """Set some instance attributes used in later logic."""
        super().setup(request, *args, **kwargs)
        self.school_id = request.user.profile.school.school_access_key

        self.model_instance_id = kwargs[self.object_id_name]
        self.model_instance = self._get_object_or_404(self.model_instance_id)

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the model instance to the form kwargs so the values can be set as initials."""
        kwargs = super().get_form_kwargs()
        kwargs["school_id"] = self.school_id
        kwargs["initial"] = self._get_initial_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add some additional context for the template."""
        context = super().get_context_data(**kwargs)
        context["model_instance"] = self.model_instance
        context["page_url"] = self.page_url

        context["deletion_form"] = self.deletion_form_class(
            model_instance=self.model_instance
        )
        context["deletion_form_is_disabled"] = self.deletion_form_is_disabled()
        context["delete_url"] = self.delete_url

        return context

    def get_success_url(self) -> str:
        """Redirect a posted form back to the same page."""
        return self.page_url

    # --------------------
    # Helper methods
    # --------------------
    def _get_htmx_response(self) -> http.HttpResponse:
        """Get an editable update form partial."""
        template = loader.get_template(template_name=self.enabled_form_template_name)
        context = self.get_context_data()
        return http.HttpResponse(template.render(context=context, request=self.request))

    def _get_object_or_404(self, model_instance_id: int | str) -> _ModelT:
        """Retrieve the model instance we are updating."""
        try:
            return self.model_class.objects.get(
                school_id=self.school_id, **{self.object_id_name: model_instance_id}
            )
        except self.model_class.DoesNotExist:
            raise http.Http404

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
    def request_is_from_htmx(self) -> bool:
        """Whether the request being handled is an htmx request."""
        return "Http-Hx-Request" in self.request.headers.keys() or bool(
            self.request.htmx
        )

    @property
    def page_url(self) -> str:
        """Construct the full page url."""
        return self.page_url_prefix.url(
            lazy=False, **{self.object_id_name: self.model_instance_id}
        )

    @property
    def delete_url(self) -> str:
        """Construct the full url to POST to, to delete the model instance."""
        return self.delete_url_prefix.url(
            lazy=False, **{self.object_id_name: self.model_instance_id}
        )
