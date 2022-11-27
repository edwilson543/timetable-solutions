"""
Module declaring the ModelAdmin for each model registered to the custom admin site
"""
# Standard library imports

# Django imports
from django.contrib import admin

# Local application imports
from .custom_admin_site import user_admin
from .base_model_admin import CustomModelAdminBase
from data import models


@admin.register(models.Pupil, site=user_admin)
class PupilAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Pupil model
    """
    list_display = ["firstname", "surname", "year_group", "pupil_id", "get_lessons_per_week", "get_occupied_percentage"]
    list_display_links = ["firstname"]

    list_filter = ["year_group"]

    search_fields = ["firstname", "surname", "pupil_id"]
    search_help_text = "Search for a pupil by name or id"


@admin.register(models.Teacher, site=user_admin)
class TeacherAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Teacher model
    """
    list_display = ["title", "firstname", "surname", "teacher_id", "get_lessons_per_week", "get_occupied_percentage"]
    list_display_links = ["firstname"]

    search_fields = ["firstname", "surname", "teacher_id"]
    search_help_text = "Search for a teacher by name or id"


@admin.register(models.Classroom, site=user_admin)
class ClassroomAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Classroom model
    """
    list_display = ["classroom_id", "building", "room_number", "get_lessons_per_week", "get_occupied_percentage"]
    list_display_links = ["classroom_id"]

    list_filter = ["building"]

    search_fields = ["classroom_id", "building", "room_number"]
    search_help_text = "Search for a classroom by building, room number or id"


@admin.register(models.TimetableSlot, site=user_admin)
class TimetableSlotAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the TimetableSlot model
    """
    list_display = ["day_of_week", "_get_slot_time_string", "slot_id"]
    list_display_links = ["slot_id"]

    list_filter = ["day_of_week", "period_starts_at"]

    search_fields = ["day_of_week", "period_starts_at", "slot_id"]
    search_help_text = "Search for a slot by day, time, or id"

    def _get_slot_time_string(self, obj: models.TimetableSlot) -> str:
        """
        Method to provide a string combining the time slot start and end time
        """
        return obj.period_starts_at.strftime("%H:%M") + "-" + obj.period_ends_at.strftime("%H:%M")
    _get_slot_time_string.short_description = "Time"
