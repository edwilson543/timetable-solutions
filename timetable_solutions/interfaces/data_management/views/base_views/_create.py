# Standard library imports
import abc
from typing import Any, ClassVar, Generic, TypeVar

# Django imports
from django import forms as django_forms
from django import http
from django.contrib import messages
from django.contrib.auth import mixins
from django.db import models as django_models
from django.views import generic

# Local application imports
from domain.data_management import base_exceptions
from interfaces.utils.typing_utils import AuthenticatedHttpRequest

_ModelT = TypeVar("_ModelT", bound=django_models.Model)
_CreateFormT = TypeVar("_CreateFormT", bound=django_forms.Form)


class CreateView(
    mixins.LoginRequiredMixin, generic.FormView, Generic[_ModelT, _CreateFormT]
):
    """Page displaying a form to create an instance of some model."""

    # Generic class vars
    model_class: type[_ModelT]
    """The model we are updating an instance of."""

    form_class: type[_CreateFormT]
    """Form used to update a model instance (overridden from django's FormView)"""

    # Ordinary class vars
    page_url: ClassVar[str]
    """URL for this page and where the search form should be submitted."""

    success_url: ClassVar[str]
    """
    URL to redirect to on successful creation of a new model instance.
    """

    object_id_name: ClassVar[str]
    """Name of the object's id field, that is unique to the school. e.g. 'teacher_id', 'pupil_id'."""

    # Instance vars
    school_id: int
    """The school who's data will be shown."""

    created_model_instance: _ModelT | None
    """The model instance that has been created."""

    @abc.abstractmethod
    def create_model_from_clean_form(self, form: _CreateFormT) -> _ModelT:
        """Create a model instance using the clean form data."""
        raise NotImplemented

    def form_valid(self, form: _CreateFormT) -> http.HttpResponse:
        """Try to call the model creating function when we get some valid form data."""
        try:
            self.create_model_from_clean_form(form=form)
        except base_exceptions.UnableToCreateModelInstance as exc:
            form.add_error(None, error=exc.human_error_message)
            return super().form_invalid(form=form)

        msg = f"New {self.model_class.Constant.human_string_singular} successfully created!"
        messages.success(request=self.request, message=msg)
        return super().form_valid(form=form)

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> None:
        """Set some instance attributes used in later logic."""
        super().setup(request, *args, **kwargs)
        self.school_id = request.user.profile.school.school_access_key

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the school id as an init kwarg to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["school_id"] = self.school_id
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Include a queryset in the context.

        This is either the return of the user's search, or all model data for their school.
        """
        context = super().get_context_data(**kwargs)
        context["page_url"] = self.page_url
        return context
