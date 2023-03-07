"""Views for the year group data management functionality."""

# Standard library imports
from typing import Any

# Django imports
from django import http
from django.contrib import messages

# Local application imports
from data import models
from domain.data_management.year_groups import exceptions as year_group_exceptions
from domain.data_management.year_groups import operations as year_group_operations
from domain.data_management.year_groups import queries as year_group_queries
from interfaces.constants import UrlName
from interfaces.data_management import forms, serializers
from interfaces.data_management.views import base_views


class YearGroupLanding(base_views.LandingView):
    """Page users arrive at from 'data/yeargroup' on the navbar."""

    model_class = models.YearGroup

    # TODO -> update the urls once implemented
    upload_url = UrlName.TEACHER_UPLOAD
    create_url = UrlName.YEAR_GROUP_CREATE
    list_url = UrlName.YEAR_GROUP_LIST

    def has_existing_data(self) -> bool:
        return self.request.user.profile.school.has_year_group_data


class YearGroupList(base_views.ListView):
    """Page displaying all a school's year group data."""

    template_name = "data_management/year-group/year-group-list.html"
    ordering = ["year_group_id"]

    model_class = models.YearGroup
    serializer_class = serializers.YearGroup

    displayed_fields = {
        "year_group_id": "Year group ID",
        "year_group_name": "Year group name",
        "number_pupils": "Number pupils",
    }

    update_url = ""  # TODO -> add once available


class YearGroupCreate(base_views.CreateView):
    """Page allowing users to create a single year group."""

    template_name = "data_management/year-group/year-group-create.html"

    model_class = models.YearGroup
    form_class = forms.YearGroupCreate

    page_url = UrlName.YEAR_GROUP_CREATE.url(lazy=True)
    success_url_prefix = UrlName.YEAR_GROUP_UPDATE
    object_id_name = "year_group_id"

    def create_model_from_clean_form(
        self, form: forms.YearGroupCreate
    ) -> models.YearGroup | None:
        """Create a year group in the db using the clean form details."""
        year_group_id = form.cleaned_data.get("year_group_id", None)
        try:
            return year_group_operations.create_new_year_group(
                school_id=self.school_id,
                year_group_id=year_group_id,
                year_group_name=form.cleaned_data["year_group_name"],
            )
        except year_group_exceptions.CouldNotCreateYearGroup:
            return None

    def get_form_kwargs(self) -> dict[str, Any]:
        """Set the next available year group id as an initial value."""
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "year_group_id": year_group_queries.get_next_year_group_id_for_school(
                school_id=self.school_id
            )
        }
        return kwargs


class YearGroupUpdate(base_views.UpdateView):
    """Page displaying information on a single year group, allowing this data to be updated / deleted."""

    template_name = "data_management/year-group/year-group-detail-update.html"

    model_class = models.YearGroup
    form_class = forms.YearGroupUpdate
    serializer_class = serializers.YearGroup

    object_id_name = "year_group_id"
    model_attributes_for_form_initials = ["year_group_name"]
    page_url_prefix = UrlName.YEAR_GROUP_UPDATE
    delete_success_url = UrlName.YEAR_GROUP_LIST.url(lazy=True)

    def update_model_from_clean_form(
        self, form: forms.YearGroupUpdate
    ) -> models.YearGroup | None:
        """Update a year group's name in the db."""
        year_group_name = form.cleaned_data.get("year_group_name", None)
        try:
            return year_group_operations.update_year_group(
                year_group=self.model_instance,
                year_group_name=year_group_name,
            )
        except year_group_exceptions.CouldNotUpdateYearGroup:
            return None

    def delete_model_instance(self) -> http.HttpResponse:
        """Delete the Teacher stored as an instance attribute."""
        try:
            msg = f"{self.model_instance} was deleted."
            year_group_operations.delete_year_group(year_group=self.model_instance)
            messages.success(request=self.request, message=msg)
            return http.HttpResponseRedirect(self.delete_success_url)
        except year_group_exceptions.CouldNotDeleteYearGroup:
            context = super().get_context_data()
            msg = "Could not delete this year group, try deleting all associated data"
            context["deletion_error_message"] = msg
            return super().render_to_response(context=context)
