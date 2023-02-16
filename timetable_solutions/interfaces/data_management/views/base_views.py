"""View classes shared across the data management admin."""

import abc
from typing import Any, Generic, TypeVar

from django.contrib.auth import mixins
from django import forms as django_forms
from django import http
from django.db import models as django_models
from django.views import generic

from interfaces.data_management import forms


M = TypeVar("M", bound=django_models.Model)


class SearchListBase(mixins.LoginRequiredMixin, generic.FormView, Generic[M]):
    """Page displaying a school's data for one db table, and allowing them to search that table."""

    # Custom vars
    model: type[M]
    """The model who's data is rendered on this page."""

    displayed_fields: dict[str, str]
    """
    The fields to use as column headers in the rendered context.
    Given as {field name: displayed name, ...} key-value pairs.
    """

    search_help_text: str
    """User prompt for the fields they can search by."""

    form_post_url: str
    """URL the search form should be posted to."""

    school_id: int
    """The school who's data will be shown."""

    @abc.abstractmethod
    def execute_search_from_clean_form(
        self, form: django_forms.Form
    ) -> django_models.QuerySet[M]:
        """
        Retrieve a queryset of objects by calling some model-specific domain function.

        Note this must return an ordinary queryset. Conversion to the relevant subset
        of fields with .values_list() is handled by the base form_valid method.
        """
        raise NotImplemented

    def setup(self, request: http.HttpRequest, *args: object, **kwargs: object) -> None:
        """Set the school id based on the authenticated user."""
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            self.school_id = request.user.profile.school.school_access_key

    def get_form_kwargs(self) -> dict[str, Any]:
        """Set form parameters that are model specific, as defined by the class vars."""
        kwargs = super().get_form_kwargs()
        kwargs["search_help_text"] = self.search_help_text
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Include a queryset in the context.

        This is either the return of the user's search, or all model data for their school.
        """
        context = super().get_context_data(**kwargs)
        context["form_post_url"] = self.form_post_url
        context["human_field_names"] = self.human_field_names
        context["model_class"] = self.model
        # TODO HERE -> Pagination
        try:
            object_list = kwargs["object_list"]
        except KeyError:
            object_list = self.model.objects.get_all_instances_for_school(
                school_id=self.school_id
            ).values_list(*self.display_field_names)

        context["object_list"] = object_list
        return context

    def form_valid(self, form: forms.TeacherSearch) -> http.HttpResponse:
        """Get the search results and a new form which includes the search terms."""
        object_list = self.execute_search_from_clean_form(form=form).values_list(
            *self.display_field_names
        )

        new_form = self.get_form()
        # Render the new form with the current search
        for field, value in form.cleaned_data.items():
            new_form.fields[field].initial = value

        context = self.get_context_data(form=form, object_list=object_list)
        return self.render_to_response(context=context)

    # --------------------
    # Properties
    # --------------------

    @property
    def display_field_names(self) -> list[str]:
        """The field names in the database that data will be fetched from."""
        return list(self.displayed_fields.keys())

    @property
    def human_field_names(self) -> list[str]:
        """Human friendly names for each field."""
        return list(self.displayed_fields.values())
