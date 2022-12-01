"""
Module containing the custom ModelAdmin for the Profile model, and its ancillaries.
"""

# Django imports
from django.contrib import admin
from django import http

# Local application imports
from data import models
from interfaces.custom_admin.admin import user_admin
from interfaces.custom_admin.admin.base_model_admin import CustomModelAdminBase


@admin.register(models.Profile, site=user_admin)
class ProfileAdmin(CustomModelAdminBase):
    """
    ModelAdmin for the Profile model.
    """
    # Index page display
    list_display = ["user", "get_first_name", "get_last_name", "role", "approved_by_school_admin"]
    list_filter = ["role", "approved_by_school_admin"]

    search_fields = ["user__username", "user__first_name", "user__last_name"]
    search_help_text = "Search for users by username, firstname or surname"

    class Meta:
        """
        Include the Profile model as if it's in its own 'users' app.
        """
        custom_app_label = "users"

    def get_first_name(self, obj: models.Profile) -> str:
        """
        Manual extraction of the associated user's first_name, since user__first_name is disallowed in list_display
        for some reason.
        """
        return obj.user.first_name
    get_first_name.short_description = "First name"

    def get_last_name(self, obj: models.Profile) -> str:
        """
        Manual extraction of the associated user's last_name, since user__last_name is disallowed in list_display
        for some reason.
        """
        return obj.user.last_name
    get_last_name.short_description = "Surname"

    # ACTIONS - TODO

    # PERMISSIONS
    def has_add_permission(self, request: http.HttpRequest) -> bool:
        """
        It does not make sense for the admin to be able to make Profile model instances.
        """
        return False
