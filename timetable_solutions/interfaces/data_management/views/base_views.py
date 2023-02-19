"""View classes shared across the data management admin."""

import abc
from typing import Any, ClassVar, Generic, TypeVar

from django import http
from django.contrib.auth import mixins
from django.db import models as django_models
from django import forms as django_forms
from django.views import generic


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

    def setup(self, request: http.HttpRequest, *args: object, **kwargs: object) -> None:
        """Set some instance attributes used in later logic."""
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
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
