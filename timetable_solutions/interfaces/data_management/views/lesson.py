"""
Views for lesson data management.
"""

# Standard library imports
from typing import Any

# Django imports
from django.db.models import Prefetch

# Local application imports
from data import models
from domain.data_management import upload_processors
from domain.data_management.constants import ExampleFile
from domain.data_management.lesson import operations, queries
from interfaces.constants import UrlName
from interfaces.data_management import forms, serializers
from interfaces.utils import base_views


class LessonLanding(base_views.LandingView):
    """
    Page users arrive at from 'data/lesson' on the navbar.
    """

    model_class = models.Lesson

    upload_url = UrlName.LESSON_UPLOAD
    create_url = UrlName.LESSON_CREATE
    list_url = UrlName.LESSON_LIST

    def has_existing_data(self) -> bool:
        return self.school.has_lesson_data

    def cannot_add_data_reason(self) -> str | None:
        """
        Lessons depend on all other data having been added.
        """
        has_pupils = self.school.has_pupil_data
        has_slots = self.school.has_timetable_structure_data
        has_teachers = self.school.has_teacher_data
        has_classrooms = self.school.has_classroom_data
        if not (has_pupils and has_slots and has_teachers and has_classrooms):
            return "You must add some pupils, timetable slots, teachers and classrooms before you can add lessons! "
        return None


class LessonSearch(base_views.SearchView[models.Lesson, forms.LessonSearch]):
    """
    Page displaying all a school's lesson data and allowing searching this list.
    """

    template_name = "data_management/lesson/lesson-list.html"
    ordering = ["lesson_id"]

    model_class = models.Lesson
    form_class = forms.LessonSearch
    serializer_class = serializers.Lesson

    displayed_fields = {
        "lesson_id": "Lesson ID",
        "subject_name": "Lesson name",
        "year_group": "Year group",
        "teacher": "Teacher",
        "classroom": "Classroom",
        "total_required_slots": "Required slots per week",
    }
    page_url = UrlName.LESSON_LIST.url(lazy=True)

    def execute_search_from_clean_form(
        self, form: forms.LessonSearch
    ) -> models.LessonQuerySet:
        """
        Get the queryset of lessons matching the search term.
        """
        search_term = form.cleaned_data.get("search_term", None)
        return queries.get_lessons(
            school_id=self.school_id,
            search_term=search_term,
        )


class LessonCreate(base_views.CreateView[models.Lesson, forms.LessonCreate]):
    """
    Page allowing the users to create a single lesson.
    """

    template_name = "data_management/lesson/lesson-create.html"

    model_class = models.Lesson
    form_class = forms.LessonCreate

    page_url = UrlName.LESSON_CREATE.url(lazy=True)
    success_url = UrlName.LESSON_LIST.url(lazy=True)
    object_id_name = "lessonid"

    def create_model_from_clean_form(self, form: forms.LessonCreate) -> models.Lesson:
        """
        Create a lesson in the db using the clean form details.
        """
        lesson_id = form.cleaned_data.get("lesson_id", None)
        subject_name = form.cleaned_data.get("subject_name", None)
        teacher = form.cleaned_data.get("teacher", None)
        classroom = form.cleaned_data.get("classroom", None)
        year_group = form.cleaned_data.get("year_group", None)
        total_required_slots = form.cleaned_data.get("total_required_slots", None)
        total_required_double_periods = form.cleaned_data.get(
            "total_required_double_periods", None
        )
        return operations.create_new_lesson(
            school_id=self.school_id,
            lesson_id=lesson_id,
            subject_name=subject_name,
            teacher_id=teacher.teacher_id,
            classroom_id=classroom.classroom_id,
            year_group=year_group,
            total_required_slots=total_required_slots,
            total_required_double_periods=total_required_double_periods,
        )


class LessonUpdate(base_views.UpdateView[models.Lesson, forms.LessonUpdate]):
    """
    Page displaying information on a single lesson, allowing this data to be updated / deleted.
    """

    template_name = "data_management/lesson/lesson-detail-update.html"

    model_class = models.Lesson
    form_class = forms.LessonUpdate
    serializer_class = serializers.Lesson

    prefetch_related = [Prefetch("pupils"), Prefetch("user_defined_time_slots")]

    object_id_name = "lesson_id"
    model_attributes_for_form_initials = [
        "subject_name",
        "teacher",
        "classroom",
        "total_required_slots",
        "total_required_double_periods",
    ]
    page_url_prefix = UrlName.LESSON_UPDATE
    delete_success_url = UrlName.LESSON_LIST.url(lazy=True)

    def update_model_from_clean_form(self, form: forms.LessonUpdate) -> models.Lesson:
        """
        Update a lesson's details in the db.
        """
        subject_name = form.cleaned_data.get("subject_name")
        teacher = form.cleaned_data.get("teacher")
        classroom = form.cleaned_data.get("classroom")
        total_required_slots = form.cleaned_data.get("total_required_slots")
        total_required_double_periods = form.cleaned_data.get(
            "total_required_double_periods"
        )
        return operations.update_lesson(
            lesson=self.model_instance,
            subject_name=subject_name,
            teacher=teacher,
            classroom=classroom,
            total_required_slots=total_required_slots,
            total_required_double_periods=total_required_double_periods,
        )

    def delete_model_instance(self) -> None:
        """
        Delete the lesson stored as an instance attribute.
        """
        operations.delete_lesson(lesson=self.model_instance)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["lesson"] = self.model_instance
        return kwargs


class LessonUpdatePupilsPartial(
    base_views.UpdateRelatedListPartialView[models.Lesson, models.Pupil]
):
    """
    Partial allowing users to view and add pupils to a lesson.
    """

    model_class = models.Lesson
    form_class = forms.LessonAddPupil
    object_id_name = "lesson_id"
    page_url_prefix = UrlName.LESSON_UPDATE_PUPILS_PARTIAL

    # Related object vars
    related_name = "pupils"
    related_model_name = "Pupils"
    related_object_id_name = "pupil_id"
    related_model_class = models.Pupil

    serializer_class = serializers.Pupil
    displayed_fields = {
        "pupil_id": "Pupil ID",
        "firstname": "Firstname",
        "surname": "Surname",
    }
    ordering = ["pupil_id"]

    def add_related_object(self, form: forms.LessonAddPupil) -> None:
        """
        Try adding a pupil to the lesson.
        """
        pupil = form.cleaned_data["pupil"]
        self.model_instance.add_pupil(pupil=pupil)

    def remove_related_object(self, related_model_instance: models.Pupil) -> None:
        """
        Remove a teacher form a lesson.
        """
        self.model_instance.remove_pupil(pupil=related_model_instance)

    def extra_form_kwargs(self) -> dict[str, Any]:
        """
        Pass the school id and lesson when instantiating the form.
        """
        return {"school_id": self.school_id, "lesson": self.model_instance}


class LessonUpdateUserDefinedTimetableSlotPartial(
    base_views.UpdateRelatedListPartialView[models.Lesson, models.TimetableSlot]
):
    """
    Partial allowing users to view and add pre-defined timetable slots to a lesson.
    """

    model_class = models.Lesson
    form_class = forms.LessonAddUserDefinedTimetableSlot
    object_id_name = "lesson_id"
    page_url_prefix = UrlName.LESSON_UPDATE_USER_SLOTS_PARTIAL

    # Related object vars
    related_name = "user_defined_time_slots"
    related_model_name = "Timetable slots"
    related_object_id_name = "slot_id"
    related_model_class = models.TimetableSlot

    serializer_class = serializers.TimetableSlot
    displayed_fields = {
        "slot_id": "Slot ID",
        "day_of_week": "Day of week",
        "starts_at": "Starts at",
        "ends_at": "Ends at",
    }
    ordering = ["slot_id"]

    def add_related_object(self, form: forms.LessonAddUserDefinedTimetableSlot) -> None:
        """
        Try adding a pupil to the lesson.
        """
        slot = form.cleaned_data["slot"]
        self.model_instance.add_user_defined_time_slot(slot=slot)

    def remove_related_object(
        self, related_model_instance: models.TimetableSlot
    ) -> None:
        """
        Remove a teacher form a lesson.
        """
        self.model_instance.remove_user_defined_time_slot(slot=related_model_instance)

    def extra_form_kwargs(self) -> dict[str, Any]:
        """
        Pass the school id and lesson when instantiating the form.
        """
        return {"school_id": self.school_id, "lesson": self.model_instance}


class LessonUpload(base_views.UploadView):
    """
    Allow users to upload a csv file containing lesson data.
    """

    template_name = "data_management/lesson/lesson-upload.html"
    success_url = UrlName.LESSON_LIST.url(lazy=True)

    upload_processor_class = upload_processors.LessonFileUploadProcessor
    upload_url = UrlName.LESSON_UPLOAD.url(lazy=True)
    example_download_url = UrlName.LESSON_DOWNLOAD.url(lazy=True)


class LessonExampleDownload(base_views.ExampleDownloadBase):
    """
    Provide a response when users want to download an example lesson file.
    """

    example_filepath = ExampleFile.LESSON.filepath
