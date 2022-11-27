"""
Module containing the custom ModelAdmin for the Lesson model, and its ancillaries.
This gets its own module since the Lesson model itself is more complex, passing this complexity on to the admin.
"""

# Standard library imports
from typing import List

# Django imports
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

    def lookups(self, request: http.HttpRequest, model_admin) -> List:
        """
        Returns a list of tuples, whose first entry is the subject name as stored in the database, and the second
        subject name to show to the user. Subject names are used as the filters.
        """
        unique_subjects = set(self.get_unfiltered_queryset(request=request).values_list("subject_name", flat=True))
        subject_names = [
            (subject_name, clean_string(subject_name)) for subject_name in unique_subjects
        ]
        return subject_names

    def queryset(self, request: http.HttpRequest, queryset: models.LessonQuerySet) -> models.LessonQuerySet:
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
        return models.Lesson.objects.get_all_instances_for_school(school_id=school_access_key)


@admin.register(models.Lesson, site=user_admin)
class LessonAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Lesson model
    """
    list_display = ["format_lesson_id", "format_subject_name", "format_teacher",
                    "number_pupils", "format_total_required_slots"]
    list_filter = [SubjectNameFilter]
    search_fields = ["lesson_id", "subject_name", "teacher", "pupils"]
    search_help_text = "Search for lessons by id, subject name, teacher or pupils"

    # List display fields
    def format_lesson_id(self, obj: models.Lesson) -> str:
        """
        Method to format the lesson id more nicely for the user.
        """
        return clean_string(string=obj.lesson_id)
    format_lesson_id.short_description = "Lesson ID"

    def format_subject_name(self, obj: models.Lesson) -> str:
        """
        Method to format the subject_name more nicely for the user.
        """
        return clean_string(string=obj.subject_name)
    format_subject_name.short_description = "Subject"

    def format_teacher(self, obj: models.Lesson) -> str:
        """
        Method to format the teacher's string representation different to the Teacher model's __str__ method
        """
        if obj.teacher is not None:
            teacher = obj.teacher
            return f"{teacher.title} {teacher.surname}, {teacher.firstname}"
        else:
            return "N/A"
    format_teacher.short_description = "Teacher"

    def number_pupils(self, obj: models.Lesson) -> SafeString:
        """
        Method to retrieve the number of pupils in a Lesson, for the admin.
        """
        pupil_count = obj.pupils.all().count()
        return html.format_html(f"<b><i>{pupil_count}</i></b>")
    number_pupils.short_description = "Number pupils"

    def format_total_required_slots(self, obj: models.Lesson) -> str:
        """
        Method formatting the number of lessons a Lesson is taught for each week, to be displayed in the admin.
        """
        slot_count = obj.total_required_slots
        return html.format_html(f"<b><i>{slot_count}<i><b>")
    format_total_required_slots.short_description = "Lessons per week"


def clean_string(string: str) -> str:
    """
    Method to convert underscores to spaces and capitalise only the first letter of a string
    """
    string = string.replace("_", " ")
    string = string.title()
    return string
