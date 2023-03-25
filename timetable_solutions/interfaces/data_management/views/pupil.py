"""
Views for pupil data management.
"""

# Standard library imports
from typing import Any

# Django imports
from django.db.models import Prefetch

# Local application imports
from data import models
from domain.data_management import upload_processors
from domain.data_management.constants import ExampleFile
from domain.data_management.pupils import operations, queries
from interfaces.constants import UrlName
from interfaces.data_management import forms, serializers
from interfaces.utils import base_views


class PupilLanding(base_views.LandingView):
    """
    Page users arrive at from 'data/pupils' on the navbar.
    """

    model_class = models.Pupil

    upload_url = UrlName.PUPIL_UPLOAD
    create_url = UrlName.PUPIL_CREATE
    list_url = UrlName.PUPIL_LIST

    def has_existing_data(self) -> bool:
        return self.request.user.profile.school.has_pupil_data

    def cannot_add_data_reason(self) -> str | None:
        if not self.school.has_year_group_data:
            return "You must add some year groups before you can add pupils!"
        return None


class PupilSearch(base_views.SearchView):
    """
    Page displaying all a school's pupil data and allowing them to search for pupils.
    """

    template_name = "data_management/pupil/pupil-list.html"
    ordering = ["pupil_id"]

    model_class = models.Pupil
    form_class = forms.PupilSearch
    serializer_class = serializers.Pupil

    displayed_fields = {
        "pupil_id": "Pupil ID",
        "firstname": "Firstname",
        "surname": "Surname",
        "year_group": "Year group",
    }
    page_url = UrlName.PUPIL_LIST.url(lazy=True)
    update_url = UrlName.PUPIL_UPDATE

    def execute_search_from_clean_form(
        self, form: forms.PupilSearch
    ) -> models.PupilQuerySet:
        """
        Get the queryset of pupils matching the search term.
        """
        search_term = form.cleaned_data.get("search_term", None)
        year_group = form.cleaned_data.get("year_group", None)
        return queries.get_pupils(
            school_id=self.school_id, search_term=search_term, year_group=year_group
        )

    def get_form_kwargs(self) -> dict[str, int]:
        """
        Provide the school_id when instantiating the search form.
        """
        return {"school_id": self.school_id}


class PupilCreate(base_views.CreateView):
    """
    Page allowing the users to create a single pupil.
    """

    template_name = "data_management/pupil/pupil-create.html"

    model_class = models.Pupil
    form_class = forms.PupilCreate

    page_url = UrlName.PUPIL_CREATE.url(lazy=True)
    success_url = UrlName.PUPIL_LIST.url(lazy=True)
    object_id_name = "pupil_id"

    def create_model_from_clean_form(
        self, form: forms.PupilCreate
    ) -> models.Pupil | None:
        """
        Create a pupil in the db using the clean form details.
        """
        pupil_id = form.cleaned_data.get("pupil_id", None)
        return operations.create_new_pupil(
            school_id=self.school_id,
            pupil_id=pupil_id,
            firstname=form.cleaned_data["firstname"],
            surname=form.cleaned_data["surname"],
            year_group_id=form.cleaned_data["year_group"].year_group_id,
        )

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Set the next available pupil id as an initial value.
        """
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "pupil_id": queries.get_next_pupil_id_for_school(school_id=self.school_id)
        }
        return kwargs


class PupilUpdate(base_views.UpdateView):
    """
    Page displaying information on a single pupil, allowing this data to be updated / deleted.
    """

    template_name = "data_management/pupil/pupil-detail-update.html"

    model_class = models.Pupil
    form_class = forms.PupilUpdate
    serializer_class = serializers.Pupil

    prefetch_related = [Prefetch("lessons")]

    object_id_name = "pupil_id"
    model_attributes_for_form_initials = ["firstname", "surname", "year_group"]
    page_url_prefix = UrlName.PUPIL_UPDATE
    delete_success_url = UrlName.PUPIL_LIST.url(lazy=True)

    def update_model_from_clean_form(self, form: forms.PupilUpdate) -> models.Pupil:
        """
        Update a pupil's details in the db.
        """
        firstname = form.cleaned_data.get("firstname", None)
        surname = form.cleaned_data.get("surname", None)
        year_group = form.cleaned_data.get("year_group", None)
        return operations.update_pupil(
            pupil=self.model_instance,
            firstname=firstname,
            surname=surname,
            year_group=year_group,
        )

    def delete_model_instance(self) -> None:
        """
        Delete the Pupil stored as an instance attribute.
        """
        operations.delete_pupil(pupil=self.model_instance)


class PupilLessonsPartial(base_views.RelatedListPartialView):
    """
    Render a table showing the lessons this pupil has.
    """

    model_class = models.Pupil
    related_name = "lessons"
    related_model_name = "Lessons"
    object_id_name = "pupil_id"
    page_url_prefix = UrlName.PUPIL_LESSONS_PARTIAL
    serializer_class = serializers.Lesson
    displayed_fields = {
        "lesson_id": "Lesson ID",
        "subject_name": "Subject",
        "year_group": "Year group",
        "teacher": "Teacher",
        "classroom": "Classroom",
        "total_required_slots": "Lessons / week",
    }
    ordering = ["lesson_id"]


class PupilUpload(base_views.UploadView):
    """
    Page allowing users to upload a csv file containing pupil data.
    """

    template_name = "data_management/pupil/pupil-upload.html"
    success_url = UrlName.PUPIL_LIST.url(lazy=True)

    upload_processor_class = upload_processors.PupilFileUploadProcessor
    upload_url = UrlName.PUPIL_UPLOAD.url(lazy=True)
    example_download_url = UrlName.PUPIL_DOWNLOAD.url(lazy=True)


class PupilExampleDownload(base_views.ExampleDownloadBase):
    """
    Provide a response when users want to download an example pupil data file.
    """

    example_filepath = ExampleFile.PUPILS.filepath
