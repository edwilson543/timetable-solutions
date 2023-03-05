"""Views for the teacher data management functionality."""

# Standard library imports
from typing import Any

# Django imports
from django import http
from django.contrib import messages

# Local application imports
from data import models
from domain.data_management import upload_processors
from domain.data_management.constants import ExampleFile
from domain.data_management.teachers import exceptions as teacher_exceptions
from domain.data_management.teachers import operations as teacher_operations
from domain.data_management.teachers import queries as teacher_queries
from interfaces.constants import UrlName
from interfaces.data_management import forms, serializers
from interfaces.data_management.views import base_views


class TeacherLanding(base_views.LandingView):
    """Page users arrive at from 'data/teachers' on the navbar."""

    model_class = models.Teacher

    upload_url = UrlName.TEACHER_UPLOAD
    create_url = UrlName.TEACHER_CREATE
    list_url = UrlName.TEACHER_LIST

    def has_existing_data(self) -> bool:
        return self.request.user.profile.school.has_teacher_data


class TeacherSearch(base_views.SearchView):
    """Page displaying all a school's teacher data and allowing them to search for teachers."""

    template_name = "data_management/teacher/teacher-list.html"
    ordering = ["teacher_id"]

    model_class = models.Teacher
    form_class = forms.TeacherSearch
    serializer_class = serializers.Teacher

    displayed_fields = {
        "teacher_id": "Teacher ID",
        "firstname": "Firstname",
        "surname": "Surname",
        "title": "Title",
    }
    search_help_text = "Search for a teacher by name or id."
    page_url = UrlName.TEACHER_LIST.url(lazy=True)
    update_url = UrlName.TEACHER_UPDATE

    def execute_search_from_clean_form(
        self, form: forms.TeacherSearch
    ) -> models.TeacherQuerySet:
        """Get the queryset of teachers matching the search term."""
        search_term = form.cleaned_data["search_term"]
        return teacher_queries.get_teachers_by_search_term(
            school_id=self.school_id, search_term=search_term
        )


class TeacherCreate(base_views.CreateView):
    """Page allowing the users to create a single teacher."""

    template_name = "data_management/teacher/teacher-create.html"

    model_class = models.Teacher
    form_class = forms.TeacherCreate

    page_url = UrlName.TEACHER_CREATE.url(lazy=True)
    success_url_prefix = UrlName.TEACHER_UPDATE
    object_id_name = "teacher_id"

    def create_model_from_clean_form(
        self, form: forms.TeacherCreate
    ) -> models.Teacher | None:
        """Create a teacher in the db using the clean form details."""
        teacher_id = form.cleaned_data.get("teacher_id", None)
        try:
            return teacher_operations.create_new_teacher(
                school_id=self.school_id,
                teacher_id=teacher_id,
                firstname=form.cleaned_data["firstname"],
                surname=form.cleaned_data["surname"],
                title=form.cleaned_data["title"],
            )
        except teacher_exceptions.CouldNotCreateTeacher:
            return None

    def get_form_kwargs(self) -> dict[str, Any]:
        """Set the next available teacher id as an initial value."""
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "teacher_id": teacher_queries.get_next_teacher_id_for_school(
                school_id=self.school_id
            )
        }
        return kwargs


class TeacherUpdate(base_views.UpdateView):
    """Page displaying information on a single teacher, allowing this data to be updated / deleted."""

    template_name = "data_management/teacher/teacher-detail-update.html"

    model_class = models.Teacher
    form_class = forms.TeacherUpdate

    object_id_name = "teacher_id"
    model_attributes_for_form_initials = ["firstname", "surname", "title"]
    page_url_prefix = UrlName.TEACHER_UPDATE
    delete_success_url = UrlName.TEACHER_LIST.url(lazy=True)

    def update_model_from_clean_form(
        self, form: forms.TeacherUpdate
    ) -> models.Teacher | None:
        """Update a teacher's details in the db."""
        firstname = form.cleaned_data.get("firstname", None)
        surname = form.cleaned_data.get("surname", None)
        title = form.cleaned_data.get("title", None)
        try:
            return teacher_operations.update_teacher(
                teacher=self.model_instance,
                firstname=firstname,
                surname=surname,
                title=title,
            )
        except teacher_exceptions.CouldNotUpdateTeacher:
            return None

    def delete_model_instance(self) -> http.HttpResponse:
        """Delete the Teacher stored as an instance attribute."""
        try:
            msg = f"{self.model_instance} was deleted."
            teacher_operations.delete_teacher(teacher=self.model_instance)
            messages.success(request=self.request, message=msg)
            return http.HttpResponseRedirect(self.delete_success_url)
        except teacher_exceptions.CouldNotDeleteTeacher:
            msg = (
                "This teacher is still assigned to at least one lesson!\n"
                "To delete this teacher, first delete or reassign their lessons"
            )
            context = super().get_context_data()
            context["deletion_error_message"] = msg
            return super().render_to_response(context=context)


class TeacherUpload(base_views.UploadView):
    """Page allowing users to upload a csv file containing teacher data."""

    template_name = "data_management/teacher/teacher-upload.html"
    success_url = UrlName.TEACHER_LIST.url(lazy=True)

    upload_processor_class = upload_processors.TeacherFileUploadProcessor
    upload_url = UrlName.TEACHER_UPLOAD.url(lazy=True)
    example_download_url = UrlName.TEACHER_DOWNLOAD.url(lazy=True)


class TeacherExampleDownload(base_views.ExampleDownloadBase):
    """Provide a response when users want to download an example teacher data file."""

    example_filepath = ExampleFile.TEACHERS.filepath
