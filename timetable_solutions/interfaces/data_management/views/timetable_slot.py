"""
Views for timetable slot data management.
"""

# Standard library imports
from typing import Any

# Django imports
from django.db.models import Prefetch

# Local application imports
from data import models
from domain.data_management import upload_processors
from domain.data_management.constants import ExampleFile
from domain.data_management.timetable_slot import operations, queries
from interfaces.constants import UrlName
from interfaces.data_management import forms, serializers
from interfaces.data_management.views import base_views


class TimetableSlotLanding(base_views.LandingView):
    """
    Page users arrive at from 'data/timetable slot' on the navbar.
    """

    model_class = models.TimetableSlot

    upload_url = UrlName.TIMETABLE_SLOT_UPLOAD
    create_url = UrlName.TIMETABLE_SLOT_CREATE
    list_url = UrlName.TIMETABLE_SLOT_LIST

    def has_existing_data(self) -> bool:
        return self.request.user.profile.school.has_timetable_structure_data

    def cannot_add_data_reason(self) -> str | None:
        if not self.school.has_year_group_data:
            return (
                "You must add some year groups before you can add timetable slots! "
                "This is because timetable slots must be assigned to one or more year group."
            )
        return None


class TimetableSlotSearch(base_views.SearchView):
    """
    Page displaying all a school's timetable slot data and allowing them to search this list.
    """

    template_name = "data_management/timetable-slot/timetable-slot-list.html"
    ordering = ["slot_id"]

    model_class = models.TimetableSlot
    form_class = forms.TimetableSlotSearch
    serializer_class = serializers.TimetableSlot

    displayed_fields = {
        "slot_id": "Slot ID",
        "day_of_week": "Day of week",
        "starts_at": "Starts at",
        "ends_at": "Ends at",
    }
    page_url = UrlName.TIMETABLE_SLOT_LIST.url(lazy=True)
    update_url = UrlName.TIMETABLE_SLOT_UPDATE

    def execute_search_from_clean_form(
        self, form: forms.TimetableSlotSearch
    ) -> models.TimetableSlotQuerySet:
        """
        Get the queryset of timetable slots matching the search term.
        """
        slot_id = form.cleaned_data.get("slot_id", None)
        day_of_week = form.cleaned_data.get("day_of_week", None)
        year_group = form.cleaned_data.get("year_group", None)
        return queries.get_timetable_slots(
            school_id=self.school_id,
            slot_id=slot_id,
            day=day_of_week,
            year_group=year_group,
        )

    def get_form_kwargs(self) -> dict[str, int]:
        """
        Provide the school_id when instantiating the search form.
        """
        return {"school_id": self.school_id}


class TimetableSlotCreate(base_views.CreateView):
    """
    Page allowing the users to create a single timetable slot.
    """

    template_name = "data_management/timetable-slot/timetable-slot-create.html"

    model_class = models.TimetableSlot
    form_class = forms.TimetableSlotCreate

    page_url = UrlName.TIMETABLE_SLOT_CREATE.url(lazy=True)
    success_url = UrlName.TIMETABLE_SLOT_LIST.url(lazy=True)
    object_id_name = "slot_id"

    def create_model_from_clean_form(
        self, form: forms.TimetableSlotCreate
    ) -> models.TimetableSlot | None:
        """
        Create a timetable slot in the db using the clean form details.
        """
        slot_id = form.cleaned_data.get("slot_id", None)
        return operations.create_new_timetable_slot(
            school_id=self.school_id,
            slot_id=slot_id,
            day_of_week=form.cleaned_data["day_of_week"],
            starts_at=form.cleaned_data["starts_at"],
            ends_at=form.cleaned_data["ends_at"],
            relevant_to_all_year_groups=form.cleaned_data[
                "relevant_to_all_year_groups"
            ],
        )

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Set the next available slot id as an initial value.
        """
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "slot_id": queries.get_next_slot_id_for_school(school_id=self.school_id)
        }
        return kwargs


class TimetableSlotUpdateTimings(base_views.UpdateView):
    """
    Page displaying information on a single timetable slot, allowing this data to be updated / deleted.
    """

    template_name = "data_management/timetable-slot/timetable-slot-detail-update.html"

    model_class = models.TimetableSlot
    form_class = forms.TimetableSlotUpdateTimings
    serializer_class = serializers.TimetableSlot

    prefetch_related = [Prefetch("relevant_year_groups")]

    object_id_name = "slot_id"
    model_attributes_for_form_initials = ["day_of_week", "starts_at", "ends_at"]
    page_url_prefix = UrlName.TIMETABLE_SLOT_UPDATE
    delete_success_url = UrlName.TIMETABLE_SLOT_LIST.url(lazy=True)

    def update_model_from_clean_form(
        self, form: forms.TimetableSlotUpdateTimings
    ) -> models.TimetableSlot:
        """
        Update a timetable slot's details in the db.
        """
        day_of_week = form.cleaned_data.get("day_of_week", None)
        starts_at = form.cleaned_data.get("starts_at", None)
        ends_at = form.cleaned_data.get("ends_at", None)
        return operations.update_timetable_slot_timings(
            slot=self.model_instance,
            day_of_week=day_of_week,
            starts_at=starts_at,
            ends_at=ends_at,
        )

    def delete_model_instance(self) -> None:
        """
        Delete the timetable slot stored as an instance attribute.
        """
        operations.delete_timetable_slot(slot=self.model_instance)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["slot"] = self.model_instance
        return kwargs


class TimetableSlotUpload(base_views.UploadView):
    """
    Page allowing users to upload a csv file containing timetable slot data.
    """

    template_name = "data_management/timetable-slot/timetable-slot-upload.html"
    success_url = UrlName.TIMETABLE_SLOT_LIST.url(lazy=True)

    upload_processor_class = upload_processors.TimetableSlotFileUploadProcessor
    upload_url = UrlName.TIMETABLE_SLOT_UPLOAD.url(lazy=True)
    example_download_url = UrlName.TIMETABLE_SLOT_DOWNLOAD.url(lazy=True)


class TimetableSlotExampleDownload(base_views.ExampleDownloadBase):
    """
    Provide a response when users want to download an example timetable slot data file.
    """

    example_filepath = ExampleFile.TIMETABLE.filepath
