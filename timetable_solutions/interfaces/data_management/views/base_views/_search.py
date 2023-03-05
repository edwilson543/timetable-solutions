# Standard library imports
import abc
from typing import Any, ClassVar, Generic, TypeVar

# Django imports
from django import forms as django_forms
from django.db import models as django_models

# Local application imports
from interfaces.utils.typing_utils import AuthenticatedHttpRequest

from ._list import ListView

_ModelT = TypeVar("_ModelT", bound=django_models.Model)
_SearchFormT = TypeVar("_SearchFormT", bound=django_forms.Form)


class SearchView(ListView, Generic[_ModelT, _SearchFormT]):
    """
    Page displaying a school's data for a single model, and allowing this data to be searched.

    Searches should be sent as GET requests from <input name='search-submit' ...> tags.
    """

    # Generic class vars
    model_class: type[_ModelT]
    """The model who's data is rendered on this page."""

    form_class: type[_SearchFormT]
    """The form class used to process the user's search."""

    # Ordinary class vars
    page_url: ClassVar[str]
    """URL for this page and where the search form should be submitted."""

    search_help_text: ClassVar[str]
    """User prompt for the fields they can search by."""

    form: _SearchFormT
    """
    The form instance to be provided as context.

    If the user has submitted a search, this is validated.
    Otherwise it's just an empty instance of the form class.
    """

    @abc.abstractmethod
    def execute_search_from_clean_form(
        self, form: _SearchFormT
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
        self.form = self.get_form()

    def get_form(self) -> _SearchFormT:
        """If the user searched something, filter the queryset, otherwise return all data."""
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
            return super().get_queryset()

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Include a queryset in the context.

        This is either the return of the user's search, or all model data for their school.
        """
        context = super().get_context_data(**kwargs)
        context["page_url"] = self.page_url
        context["form"] = self.form
        return context

    # --------------------
    # Properties
    # --------------------
    @property
    def is_search(self) -> bool:
        """Whether the request includes a search attempt or not."""
        return "search-submit" in self.request.GET.keys()
