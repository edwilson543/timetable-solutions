"""
Views for timetable break_ data management.
"""

# Standard library imports
from typing import Any

# Django imports
from django import http, shortcuts
from django.contrib import messages
from django.db.models import Prefetch

# Local application imports
from data import models
from domain.data_management import upload_processors
from domain.data_management.break_ import operations, queries
from domain.data_management.constants import ExampleFile
from interfaces.constants import UrlName
from interfaces.data_management import forms, serializers
from interfaces.utils import base_views
from interfaces.utils.typing_utils import AuthenticatedHttpRequest


class BreakLanding(base_views.LandingView):
    """
    Page users arrive at from 'data/break' on the navbar.
    """

    model_class = models.Break

    upload_url = UrlName.BREAK_UPLOAD
    create_url = UrlName.BREAK_CREATE
    list_url = UrlName.BREAK_LIST

    def has_existing_data(self) -> bool:
        return self.request.user.profile.school.has_break_data

    def cannot_add_data_reason(self) -> str | None:
        has_year_groups = self.school.has_year_group_data
        has_teachers = self.school.has_teacher_data
        if not (has_year_groups and has_teachers):
            return (
                "You must add some year groups and teachers before you can add breaks! "
            )
        return None


class BreakSearch(base_views.SearchView[models.Break, forms.BreakSearch]):
    """
    Page displaying all a school's break data and allowing searching this list.
    """

    template_name = "data_management/break/break-list.html"
    ordering = ["break_id"]

    model_class = models.Break
    form_class = forms.BreakSearch
    serializer_class = serializers.Break

    displayed_fields = {
        "break_id": "Break ID",
        "break_name": "Break name",
        "day_of_week": "Day of week",
        "starts_at": "Starts at",
        "ends_at": "Ends at",
    }
    page_url = UrlName.BREAK_LIST.url(lazy=True)

    def execute_search_from_clean_form(
        self, form: forms.BreakSearch
    ) -> models.BreakQuerySet:
        """
        Get the queryset of breaks matching the search term.
        """
        search_term = form.cleaned_data.get("search_term", None)
        day_of_week = form.cleaned_data.get("day_of_week", None)
        year_group = form.cleaned_data.get("year_group", None)
        return queries.get_breaks(
            school_id=self.school_id,
            search_term=search_term,
            day=day_of_week,
            year_group=year_group,
        )

    def get_form_kwargs(self) -> dict[str, int]:
        """
        Provide the school_id when instantiating the search form.
        """
        return {"school_id": self.school_id}


class BreakCreate(base_views.CreateView[models.Break, forms.BreakCreate]):
    """
    Page allowing the users to create a single break.
    """

    template_name = "data_management/break/break-create.html"

    model_class = models.Break
    form_class = forms.BreakCreate

    page_url = UrlName.BREAK_CREATE.url(lazy=True)
    success_url = UrlName.BREAK_LIST.url(lazy=True)
    object_id_name = "break_id"

    def create_model_from_clean_form(self, form: forms.BreakCreate) -> models.Break:
        """
        Create a break in the db using the clean form details.
        """
        break_id = form.cleaned_data.get("break_id", None)
        return operations.create_new_break(
            school_id=self.school_id,
            break_id=break_id,
            break_name=form.cleaned_data["break_name"],
            day_of_week=form.cleaned_data["day_of_week"],
            starts_at=form.cleaned_data["starts_at"],
            ends_at=form.cleaned_data["ends_at"],
            relevant_to_all_year_groups=form.cleaned_data[
                "relevant_to_all_year_groups"
            ],
            relevant_to_all_teachers=form.cleaned_data["relevant_to_all_teachers"],
        )


class BreakUpdate(base_views.UpdateView[models.Break, forms.BreakUpdateTimings]):
    """
    Page displaying information on a single break, allowing this data to be updated / deleted.
    """

    template_name = "data_management/break/break-detail-update.html"

    model_class = models.Break
    form_class = forms.BreakUpdateTimings
    serializer_class = serializers.Break

    prefetch_related = [Prefetch("relevant_year_groups"), Prefetch("teachers")]

    object_id_name = "break_id"
    model_attributes_for_form_initials = [
        "break_name",
        "day_of_week",
        "starts_at",
        "ends_at",
    ]
    page_url_prefix = UrlName.BREAK_UPDATE
    delete_success_url = UrlName.BREAK_LIST.url(lazy=True)

    UPDATE_YEAR_GROUPS_SUBMIT = "update-year-groups-submit"

    def post(
        self, request: AuthenticatedHttpRequest, *args: object, **kwargs: object
    ) -> http.HttpResponse:
        """
        Override to allow handling of an additional form.
        """
        if self._is_update_year_groups_request:
            return self._handle_update_year_groups_request()
        return super().post(request, *args, **kwargs)

    def update_model_from_clean_form(
        self, form: forms.BreakUpdateTimings
    ) -> models.Break:
        """
        Update a break's details in the db.
        """
        break_name = form.cleaned_data.get("break_name", None)
        day_of_week = form.cleaned_data.get("day_of_week", None)
        starts_at = form.cleaned_data.get("starts_at", None)
        ends_at = form.cleaned_data.get("ends_at", None)
        return operations.update_break_timings(
            break_=self.model_instance,
            break_name=break_name,
            day_of_week=day_of_week,
            starts_at=starts_at,
            ends_at=ends_at,
        )

    def delete_model_instance(self) -> None:
        """
        Delete the break stored as an instance attribute.
        """
        operations.delete_break(break_=self.model_instance)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """
        Add a second form for updating this break's year groups.
        """
        context = super().get_context_data(**kwargs)
        if not kwargs.get("update_year_groups_form"):
            context["update_year_groups_form"] = self._get_update_year_groups_form()
        context["update_year_groups_submit"] = self.UPDATE_YEAR_GROUPS_SUBMIT
        return context

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["break_"] = self.model_instance
        return kwargs

    # --------------------
    # Handle the second form for updating the timetable break_'s relevant year groups
    # --------------------

    def _handle_update_year_groups_request(self) -> http.HttpResponse:
        """ "
        Try to update the year groups assigned to this break based on the user's selection.
        """
        form = self._get_update_year_groups_form()
        if form.is_valid():
            try:
                operations.update_break_year_groups(
                    break_=self.model_instance,
                    relevant_year_groups=form.cleaned_data["relevant_year_groups"],
                )
                messages.success(
                    self.request,
                    message="Relevant year groups for this break were updated!",
                )
                return shortcuts.redirect(self._get_update_year_groups_success_url())
            except operations.UnableToUpdateBreakYearGroups as exc:
                form.add_error(field=None, error=exc.human_error_message)

        return self.render_to_response(
            context=self.get_context_data(update_year_groups_form=form)
        )

    def _get_update_year_groups_form(self) -> forms.BreakUpdateYearGroups:
        """
        Get the form used for updating the year groups assigned to a break.
        """
        return forms.BreakUpdateYearGroups(**self._get_update_year_groups_form_kwargs())

    def _get_update_year_groups_form_kwargs(self) -> dict[str, Any]:
        kwargs = super(base_views.UpdateView, self).get_form_kwargs()
        kwargs["school_id"] = self.school_id
        kwargs["break_"] = self.model_instance
        if not self._is_update_year_groups_request:
            # Do not bind any data or files to this form
            kwargs.pop("data", None)
            kwargs.pop("files", None)
        return kwargs

    def _get_update_year_groups_success_url(self) -> str:
        """
        Redirect to the update view of the targeted timetable break_.
        """
        return UrlName.BREAK_UPDATE.url(break_id=self.model_instance.break_id)

    @property
    def _is_update_year_groups_request(self) -> bool:
        """
        Test whether the user has submitted the relevant year groups form.
        """
        return self.UPDATE_YEAR_GROUPS_SUBMIT in self.request.POST


class BreakUpdateRelatedTeachersPartial(
    base_views.UpdateRelatedListPartialView[models.Break, models.Teacher]
):
    """
    Partial allowing users to view and add teachers to a break.
    """

    model_class = models.Break
    form_class = forms.BreakAddTeacher
    object_id_name = "break_id"
    page_url_prefix = UrlName.BREAK_ADD_TEACHERS_PARTIAL

    # Related object vars
    related_name = "teachers"
    related_model_name = "Teachers"
    related_object_id_name = "teacher_id"
    related_model_class = models.Teacher

    serializer_class = serializers.Teacher
    displayed_fields = {
        "teacher_id": "Teacher ID",
        "firstname": "Firstname",
        "surname": "Surname",
        "title": "Title",
    }
    ordering = ["teacher_id"]

    def add_related_object(self, form: forms.BreakAddTeacher) -> None:
        """
        Try adding a teacher to the break.
        """
        teacher = form.cleaned_data["teacher"]
        operations.add_teacher_to_break(break_=self.model_instance, teacher=teacher)

    def remove_related_object(self, related_model_instance: models.Teacher) -> None:
        """
        Remove a teacher form a break.
        """
        operations.remove_teacher_from_break(
            break_=self.model_instance, teacher=related_model_instance
        )

    def extra_form_kwargs(self) -> dict[str, Any]:
        """
        Make sure the break is passed when instantiating the form.
        """
        return {"break_": self.model_instance}


class BreakUpload(base_views.UploadView):
    """
    Page allowing users to upload a csv file containing break data.
    """

    template_name = "data_management/break/break-upload.html"
    success_url = UrlName.BREAK_LIST.url(lazy=True)

    upload_processor_class = upload_processors.BreakFileUploadProcessor
    upload_url = UrlName.BREAK_UPLOAD.url(lazy=True)
    example_download_url = UrlName.BREAK_DOWNLOAD.url(lazy=True)


class BreakExampleDownload(base_views.ExampleDownloadBase):
    """
    Provide a response when users want to download an example break file.
    """

    example_filepath = ExampleFile.BREAK.filepath
