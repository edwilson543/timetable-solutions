# Standard library imports
import abc
from typing import Any, ClassVar, Generic, TypeVar

# Django imports
from django import forms as django_forms
from django.db import models as django_models

# Local application imports
from interfaces.utils.base_views import _list
from interfaces.utils.typing_utils import AuthenticatedHttpRequest

_ModelT = TypeVar("_ModelT", bound=django_models.Model)
_SearchFormT = TypeVar("_SearchFormT", bound=django_forms.Form)


class SearchView(_list.ListView, Generic[_ModelT, _SearchFormT]):
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
        raise NotImplementedError

    def setup(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> None:
        """
        Set some instance attributes used in later logic.
        """
        super().setup(request, *args, **kwargs)
        self.form = self.get_form()

    def get_form(self) -> _SearchFormT:
        """
        If the user searched something, filter the queryset, otherwise return all data.
        """
        if self.is_search:
            form = self.form_class(data=self.request.GET, **self.get_form_kwargs())
            form.full_clean()
            for field, value in form.cleaned_data.items():
                form.fields[field].initial = value
        else:
            form = self.form_class(**self.get_form_kwargs())
        return form

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Get kwargs used to instantiate the form class (except the search kwargs).
        """
        return {}

    def get_queryset(self) -> list[dict]:
        """Get the queryset based on the search term or retrieve the full queryset."""
        if self.form.is_valid():
            queryset = self.execute_search_from_clean_form(self.form).order_by(
                *self.ordering
            )
            return super().serialize_queryset(queryset)
        return super().get_queryset()

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Include a queryset in the context.

        This is either the return of the user's search, or all model data for their school.
        """
        context = super().get_context_data(**kwargs)
        context["is_search"] = self.is_search
        context["page_url"] = self.page_url
        context["form"] = self.form
        return context

    # --------------------
    # Properties
    # --------------------
    @property
    def is_search(self) -> bool:
        """
        Whether the request includes a search attempt or not.
        """
        return any(
            field in self.request.GET.keys() for field in self.form_class.base_fields
        )
