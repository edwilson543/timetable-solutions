"""View classes shared across the data management admin."""

import abc
from typing import Any, ClassVar, Generic, TypeVar

from django import http
from django.contrib.auth import mixins
from django.db import models as django_models
from django import forms as django_forms
from django.views import generic

from interfaces.constants import UrlName
from interfaces.utils.typing_utils import AuthenticatedHttpRequest


_ModelT = TypeVar("_ModelT", bound=django_models.Model)
_FormT = TypeVar("_FormT", bound=django_forms.Form)


class SearchView(mixins.LoginRequiredMixin, generic.ListView, Generic[_ModelT, _FormT]):
    """
    Page displaying a school's data for a single model, and allowing this data to be searched.

    Searches should be sent as GET requests from <input name='search-submit' ...> tags.
    """

    # Defaulted django vars
    paginate_by: ClassVar[int] = 50
    """Render 50 items per page, including for search results."""

    http_method_names = ["get"]
    """The searching is done via GET requests, so disallow POST."""

    # Generic class vars
    model_class: type[_ModelT]
    """The model who's data is rendered on this page."""

    form_class: type[_FormT]
    """The form class used to process the user's search."""

    # Ordinary class vars
    displayed_fields: ClassVar[dict[str, str]]
    """
    The fields to use as column headers in the rendered context.
    Given as {field name: displayed name, ...} key-value pairs.
    """

    search_help_text: ClassVar[str]
    """User prompt for the fields they can search by."""

    page_url: ClassVar[str]
    """URL for this page and where the search form should be submitted."""

    # Instance vars
    school_id: int
    """The school who's data will be shown."""

    form: _FormT
    """
    The form instance to be provided as context.

    If the user has submitted a search, this is validated.
    Otherwise it's just an empty instance of the form class.
    """

    @abc.abstractmethod
    def execute_search_from_clean_form(
        self, form: _FormT
    ) -> django_models.QuerySet[_ModelT]:
        """
        Retrieve a queryset of objects by calling some model-specific domain function.

        Note this must return an ordinary queryset. Conversion to the relevant subset
        of fields with .values_list() is handled by the base form_valid method.
        """
        raise NotImplemented

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> None:
        """Set some instance attributes used in later logic."""
        super().setup(request, *args, **kwargs)
        self.school_id = request.user.profile.school.school_access_key
        self.form = self.get_form()

    def get_form(self) -> _FormT:
        if self.is_search:
            form = self.form_class(
                search_help_text=self.search_help_text, data=self.request.GET
            )
            form.full_clean()
            for field, value in form.cleaned_data.items():
                form.fields[field].initial = value
        else:
            form = self.form_class(search_help_text=self.search_help_text)
        return form

    def get_queryset(self) -> django_models.QuerySet[_ModelT]:
        """Get the queryset based on the search term or retrieve the full queryset."""
        if self.form.is_valid():
            return self.execute_search_from_clean_form(self.form).values_list(
                *self.display_field_names
            )
        else:
            return self.model_class.objects.get_all_instances_for_school(
                school_id=self.school_id
            ).values_list(*self.display_field_names)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Include a queryset in the context.

        This is either the return of the user's search, or all model data for their school.
        """
        context = super().get_context_data(**kwargs)

        context["page_url"] = self.page_url
        context["human_field_names"] = self.human_field_names
        context["model_class"] = self.model_class
        context["form"] = self.form

        return context

    # --------------------
    # Properties
    # --------------------
    @property
    def is_search(self) -> bool:
        """Whether the request includes a search attempt or not."""
        return "search-submit" in self.request.GET.keys()

    @property
    def display_field_names(self) -> list[str]:
        """The field names in the database that data will be fetched from."""
        return list(self.displayed_fields.keys())

    @property
    def human_field_names(self) -> list[str]:
        """Human friendly names for each field."""
        return list(self.displayed_fields.values())


class UpdateView(mixins.LoginRequiredMixin, generic.FormView, Generic[_ModelT, _FormT]):
    """
    Page displaying a school's data for a single instance of a model,
    and allowing this data to be updated.
    """

    # Generic class vars
    model_class: type[_ModelT]
    """The model we are updating an instance of."""

    form_class: type[_FormT]
    """Form used to update a model instance."""

    # Ordinary class vars
    object_id_name: ClassVar[str]
    """Name of the object's id field, that is unique to the school. e.g. 'teacher_id', 'pupil_id'."""

    model_attributes_for_form_initials: ClassVar[list[str]]
    """The model attributes that should be set as the 'initial' values in the instantiated form."""

    page_url_prefix: ClassVar[UrlName]
    """
    Prefix of this page's url - where the search form should be submitted.
    The full url is constructed as page_url_prefix/<model_instance_id>.
    """

    # Instance vars
    school_id: int
    """The school who's data will be shown."""

    model_instance: _ModelT
    """The model who's data is rendered on this page."""

    model_instance_id: int | str
    """Id of the model instance, within the context of the school."""

    @abc.abstractmethod
    def update_model_from_clean_form(self, form: _FormT) -> _ModelT | None:
        """
        Method used to try to update the target model instance from a clean form.

        Should handle any exceptions, and return None if an instance could not be created.
        """
        raise NotImplemented

    # --------------------
    # Implementation of django hooks
    # --------------------

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
        return context

    # --------------------
    # Helper methods
    # --------------------

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
    def page_url(self) -> str:
        """Construct the full page url."""
        return self.page_url_prefix.url(
            lazy=False, **{self.object_id_name: self.model_instance_id}
        )
