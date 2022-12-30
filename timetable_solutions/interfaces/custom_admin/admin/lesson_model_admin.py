"""
Module containing the custom ModelAdmin for the Lesson model, and its ancillaries.
This gets its own module since the Lesson model itself is more complex, passing this complexity on to the admin.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms
from django import http
from django.contrib import admin
from django.utils import html
from django.utils.safestring import SafeString

# Local application imports
from data import models
from interfaces.custom_admin.admin import user_admin
from interfaces.custom_admin.admin.base_model_admin import CustomModelAdminBase


class SubjectNameFilter(admin.SimpleListFilter):
    """
    Custom filter to allow users to filter by the subject name (uncapitalised)
    """

    title = "Subject"
    parameter_name = "subject_name"

    def lookups(self, request: http.HttpRequest, model_admin: admin.ModelAdmin) -> list:
        """
        Returns a list of tuples, whose first entry is the subject name as stored in the database, and the second
        subject name to show to the user. Subject names are used as the filters.
        """
        unique_subjects = set(
            self.get_unfiltered_queryset(request=request).values_list(
                "subject_name", flat=True
            )
        )
        subject_names = [
            (subject_name, clean_string(subject_name))
            for subject_name in unique_subjects
        ]
        return subject_names

    def queryset(
        self, request: http.HttpRequest, queryset: models.LessonQuerySet
    ) -> models.LessonQuerySet:
        """
        Method to filter the full lesson queryset by the user's filter selection.
        """
        full_qs = self.get_unfiltered_queryset(request=request)
        subject_name = self.value()
        filtered_qs = full_qs.filter(subject_name=subject_name)
        if filtered_qs.exists():
            return filtered_qs
        else:  # When no filter is selected, we just show all the results
            return full_qs

    @staticmethod
    def get_unfiltered_queryset(request: http.HttpRequest) -> models.LessonQuerySet:
        """
        Method to get the full list of Lessons for a school.
        """
        school_access_key = request.user.profile.school.school_access_key
        return models.Lesson.objects.get_all_instances_for_school(
            school_id=school_access_key
        )


@admin.register(models.Lesson, site=user_admin)
class LessonAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Lesson model.
    """

    # Index page display
    list_display = [
        "format_lesson_id",
        "format_subject_name",
        "format_teacher",
        "number_pupils",
        "format_total_required_slots",
    ]
    list_filter = [SubjectNameFilter]
    search_fields = [
        "lesson_id",
        "subject_name",
        "teacher__firstname",
        "teacher__surname",
        "pupils__firstname",
        "pupils__surname",
    ]
    search_help_text = "Search for lessons by id, subject name, teacher, or pupil"

    # Change / add behaviour & templates
    exclude = ("school", "solver_defined_time_slots")
    change_form_template = "admin/lesson_change_add_form.html"
    add_form_template = "admin/lesson_change_add_form.html"

    def get_form(
        self,
        request: http.HttpRequest,
        obj: models.Lesson | None = None,
        change: bool = False,
        **kwargs: Any,
    ) -> forms.ModelForm:
        """
        Allow the M2M field to be optional for the user, since they may not want to add pupils / user defined time slots
        to a given lesson.
        """
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["pupils"].required = False
        form.base_fields["user_defined_time_slots"].required = False
        return form

    def save_model(
        self,
        request: http.HttpRequest,
        obj: models.Lesson,
        form: forms.ModelForm,
        change: bool,
    ) -> None:
        """
        The school is automatically added to the lesson instance from the request, and any existing SOLUTION is also
        cleared for ALL lessons, since e.g. adding a pupil to this lesson may be invalid if the pupil is bust at one
        of the user_defined_time_slots
        """
        school = request.user.profile.school
        obj.school = school
        models.Lesson.delete_solver_solution_for_school(
            school_id=school.school_access_key
        )
        obj.save()

    # List display fields
    @admin.display(description="Lesson ID")
    def format_lesson_id(self, obj: models.Lesson) -> str:
        """
        Method to format the lesson id more nicely for the user.
        """
        return clean_string(string=obj.lesson_id)

    @admin.display(description="Subject")
    def format_subject_name(self, obj: models.Lesson) -> str:
        """
        Method to format the subject_name more nicely for the user.
        """
        return clean_string(string=obj.subject_name)

    @admin.display(description="Teacher", empty_value="N/A")
    def format_teacher(self, obj: models.Lesson) -> str | None:
        """
        Method to format the teacher's string representation different to the Teacher model's __str__ method
        """
        if teacher := obj.teacher:
            return f"{teacher.title} {teacher.surname}, {teacher.firstname}"
        return None

    @admin.display(description="Number pupils")
    def number_pupils(self, obj: models.Lesson) -> SafeString:
        """
        Method to retrieve the number of pupils in a Lesson, for the admin.
        """
        pupil_count = obj.get_number_pupils()
        return html.format_html(f"<b><i>{pupil_count}</i></b>")

    @admin.display(description="Lessons per week")
    def format_total_required_slots(self, obj: models.Lesson) -> str:
        """
        Method formatting the number of lessons a Lesson is taught for each week, to be displayed in the admin.
        """
        slot_count = obj.total_required_slots
        return html.format_html(f"<b><i>{slot_count}<i><b>")


def clean_string(string: str) -> str:
    """
    Utility function to convert underscores to spaces and capitalise only the first letter of a string
    """
    string = string.replace("_", " ")
    string = string.title()
    return string
