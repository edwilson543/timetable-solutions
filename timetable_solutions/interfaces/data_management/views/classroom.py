"""
Views for classroom data management.
"""

# Standard library imports
from typing import Any

# Django imports
from django.db.models import Prefetch

# Local application imports
from data import models
from domain.data_management import upload_processors
from domain.data_management.classrooms import operations, queries
from domain.data_management.constants import ExampleFile
from interfaces.constants import UrlName
from interfaces.data_management import forms, serializers
from interfaces.utils import base_views


class ClassroomLanding(base_views.LandingView):
    """
    Page users arrive at from 'data/classrooms' on the navbar.
    """

    model_class = models.Classroom

    upload_url = UrlName.CLASSROOM_UPLOAD
    create_url = UrlName.CLASSROOM_CREATE
    list_url = UrlName.CLASSROOM_LIST

    def has_existing_data(self) -> bool:
        return self.request.user.profile.school.has_classroom_data


class ClassroomSearch(base_views.SearchView[models.Classroom, forms.ClassroomSearch]):
    """
    Page displaying all a school's classroom data and allowing them to search for classrooms.
    """

    template_name = "data_management/classroom/classroom-list.html"
    ordering = ["classroom_id"]

    model_class = models.Classroom
    form_class = forms.ClassroomSearch
    serializer_class = serializers.Classroom

    displayed_fields = {
        "classroom_id": "Classroom ID",
        "building": "Building",
        "room_number": "Room number",
    }
    page_url = UrlName.CLASSROOM_LIST.url(lazy=True)

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Provide the school_id when instantiating the search form.
        """
        return {"school_id": self.school_id}

    def execute_search_from_clean_form(
        self, form: forms.ClassroomSearch
    ) -> models.ClassroomQuerySet:
        """
        Get the queryset of classrooms matching the search term.
        """
        classroom_id = form.cleaned_data.get("classroom_id")
        building = form.cleaned_data.get("building")
        room_number = form.cleaned_data.get("room_number")
        return queries.get_classrooms(
            school_id=self.school_id,
            classroom_id=classroom_id,
            building=building,
            room_number=room_number,
        )


class ClassroomCreate(base_views.CreateView[models.Classroom, forms.ClassroomCreate]):
    """
    Page allowing the users to create a single classroom.
    """

    template_name = "data_management/classroom/classroom-create.html"

    model_class = models.Classroom
    form_class = forms.ClassroomCreate

    page_url = UrlName.CLASSROOM_CREATE.url(lazy=True)
    success_url = UrlName.CLASSROOM_LIST.url(lazy=True)
    object_id_name = "classroom_id"

    def create_model_from_clean_form(
        self, form: forms.ClassroomCreate
    ) -> models.Classroom:
        """
        Create a classroom in the db using the clean form details.
        """
        classroom_id = form.cleaned_data.get("classroom_id", None)
        return operations.create_new_classroom(
            school_id=self.school_id,
            classroom_id=classroom_id,
            building=form.cleaned_data["building"],
            room_number=form.cleaned_data["room_number"],
        )

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Set the next available classroom id as an initial value.
        """
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "classroom_id": queries.get_next_classroom_id_for_school(
                school_id=self.school_id
            )
        }
        return kwargs


class ClassroomUpdate(base_views.UpdateView[models.Classroom, forms.ClassroomUpdate]):
    """
    Page displaying information on a single classroom, allowing this data to be updated / deleted.
    """

    template_name = "data_management/classroom/classroom-detail-update.html"

    model_class = models.Classroom
    form_class = forms.ClassroomUpdate
    serializer_class = serializers.Classroom

    prefetch_related = [Prefetch("lessons")]

    object_id_name = "classroom_id"
    model_attributes_for_form_initials = ["building", "room_number"]
    page_url_prefix = UrlName.CLASSROOM_UPDATE
    delete_success_url = UrlName.CLASSROOM_LIST.url(lazy=True)

    def update_model_from_clean_form(
        self, form: forms.ClassroomUpdate
    ) -> models.Classroom:
        """Update a classroom's details in the db."""
        building = form.cleaned_data.get("building", None)
        room_number = form.cleaned_data.get("room_number", None)
        return operations.update_classroom(
            classroom=self.model_instance,
            building=building,
            room_number=room_number,
        )

    def delete_model_instance(self) -> None:
        """
        Delete the Classroom stored as an instance attribute.
        """
        operations.delete_classroom(classroom=self.model_instance)


class ClassroomLessonsPartial(
    base_views.RelatedListPartialView[models.Classroom, models.Lesson]
):
    """
    Render a table showing the lessons this classroom has.
    """

    model_class = models.Classroom
    related_name = "lessons"
    related_model_name = "Lessons"
    object_id_name = "classroom_id"
    page_url_prefix = UrlName.CLASSROOM_LESSONS_PARTIAL
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


class ClassroomUpload(base_views.UploadView):
    """
    Page allowing users to upload a csv file containing classroom data.
    """

    template_name = "data_management/classroom/classroom-upload.html"
    success_url = UrlName.CLASSROOM_LIST.url(lazy=True)

    upload_processor_class = upload_processors.ClassroomFileUploadProcessor
    upload_url = UrlName.CLASSROOM_UPLOAD.url(lazy=True)
    example_download_url = UrlName.CLASSROOM_DOWNLOAD.url(lazy=True)


class ClassroomExampleDownload(base_views.ExampleDownloadBase):
    """
    Provide a response when users want to download an example classroom data file.
    """

    example_filepath = ExampleFile.CLASSROOMS.filepath
