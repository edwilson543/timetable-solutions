"""
Module defining the 'other' ModelAdmins (i.e. not for the Lesson or User model).
These are:
    - PupilAdmin, TeacherAdmin, ClassroomAdmin, TimetableSlotAdmin
And all require minimal customisation beyond that provided by CustomModelAdminBase.
"""
# Standard library imports

# Django imports
from django.contrib import admin

# Local application imports
from .custom_admin_site import user_admin
from .base_model_admin import CustomModelAdminBase
from data import constants
from data import models


@admin.register(models.Teacher, site=user_admin)
class TeacherAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Teacher model
    """

    list_display = [
        "title",
        "firstname",
        "surname",
        "teacher_id",
        "get_lessons_per_week",
    ]
    list_display_links = ["firstname"]

    search_fields = ["firstname", "surname", "teacher_id"]
    search_help_text = "Search for a teacher by name or id"


@admin.register(models.Classroom, site=user_admin)
class ClassroomAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Classroom model
    """

    list_display = [
        "classroom_id",
        "building",
        "room_number",
        "get_lessons_per_week",
    ]
    list_display_links = ["classroom_id"]

    list_filter = ["building"]

    search_fields = ["classroom_id", "building", "room_number"]
    search_help_text = "Search for a classroom by building, room number or id"


@admin.register(models.YearGroup, site=user_admin)
class YearGroupAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Pupil model
    """

    list_display = ["year_group", "get_number_pupils"]
    list_display_links = ["year_group"]

    search_fields = [
        "year_group",
    ]
    search_help_text = "Search for a year group"

    @admin.display(description="Number of pupils")
    def get_number_pupils(self, obj: models.YearGroup) -> int:
        """
        Admin display column for a year group's number of pupils.
        """
        return obj.get_number_pupils()


@admin.register(models.Pupil, site=user_admin)
class PupilAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Pupil model
    """

    list_display = [
        "firstname",
        "surname",
        "year_group",
        "pupil_id",
        "get_lessons_per_week",
        "get_occupied_percentage",
    ]
    list_display_links = ["firstname"]

    list_filter = ["year_group"]

    search_fields = ["firstname", "surname", "pupil_id"]
    search_help_text = "Search for a pupil by name or id"


@admin.register(models.TimetableSlot, site=user_admin)
class TimetableSlotAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the TimetableSlot model
    """

    list_display = ["get_slot_time_string", "slot_id", "get_year_groups"]
    list_display_links = ["get_slot_time_string"]

    list_filter = ["day_of_week", "period_starts_at"]

    search_fields = ["day_of_week", "period_starts_at", "slot_id"]
    search_help_text = "Search for a slot by day, time, or id"

    @admin.display(description="Time")
    def get_slot_time_string(self, obj: models.TimetableSlot) -> str:
        """
        Method to provide a string combining the time slot start and end time
        """
        time = (
            obj.period_starts_at.strftime("%H:%M")
            + "-"
            + obj.period_ends_at.strftime("%H:%M")
        )
        return constants.Day(obj.day_of_week).label + ", " + time

    @admin.display(description="Year Groups")
    def get_year_groups(self, obj: models.TimetableSlot) -> str:
        """
        Method to provide a string representation of the year groups associated with a TimetableSlot.
        """
        ygs = obj.relevant_year_groups.all()
        yg_list = [f"{yg.year_group}, " for yg in ygs]
        return "".join(yg_list)[:-2]
