"""Views for the year group data management functionality."""

# Standard library imports
from typing import Any

# Local application imports
from data import models
from domain.data_management import upload_processors
from domain.data_management.constants import ExampleFile
from domain.data_management.year_groups import operations, queries
from interfaces.constants import UrlName
from interfaces.data_management import forms, serializers
from interfaces.utils import base_views


class YearGroupLanding(base_views.LandingView):
    """Page users arrive at from 'data/yeargroup' on the navbar."""

    model_class = models.YearGroup

    upload_url = UrlName.YEAR_GROUP_UPLOAD
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


class YearGroupCreate(base_views.CreateView):
    """Page allowing users to create a single year group."""

    template_name = "data_management/year-group/year-group-create.html"

    model_class = models.YearGroup
    form_class = forms.YearGroupCreate

    page_url = UrlName.YEAR_GROUP_CREATE.url(lazy=True)
    success_url = UrlName.YEAR_GROUP_LIST.url(lazy=True)
    object_id_name = "year_group_id"

    def create_model_from_clean_form(
        self, form: forms.YearGroupCreate
    ) -> models.YearGroup | None:
        """Create a year group in the db using the clean form details."""
        year_group_id = form.cleaned_data.get("year_group_id", None)
        return operations.create_new_year_group(
            school_id=self.school_id,
            year_group_id=year_group_id,
            year_group_name=form.cleaned_data["year_group_name"],
        )

    def get_form_kwargs(self) -> dict[str, Any]:
        """Set the next available year group id as an initial value."""
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "year_group_id": queries.get_next_year_group_id_for_school(
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
        return operations.update_year_group(
            year_group=self.model_instance,
            year_group_name=year_group_name,
        )

    def delete_model_instance(self) -> None:
        """Delete the Teacher stored as an instance attribute."""
        operations.delete_year_group(year_group=self.model_instance)


class YearGroupUpload(base_views.UploadView):
    """Page allowing users to upload a csv file containing year group data."""

    template_name = "data_management/year-group/year-group-upload.html"
    success_url = UrlName.YEAR_GROUP_LIST.url(lazy=True)

    upload_processor_class = upload_processors.YearGroupFileUploadProcessor
    upload_url = UrlName.YEAR_GROUP_UPLOAD.url(lazy=True)
    example_download_url = UrlName.YEAR_GROUP_DOWNLOAD.url(lazy=True)


class YearGroupExampleDownload(base_views.ExampleDownloadBase):
    """Provide a response when users want to download an example year group data file."""

    example_filepath = ExampleFile.YEAR_GROUPS.filepath
