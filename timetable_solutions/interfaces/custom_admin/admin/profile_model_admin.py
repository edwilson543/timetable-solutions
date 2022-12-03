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

    actions = ["approve_user_accounts"]

    exclude = ("school", "user")

    class Meta:
        """
        Include the Profile model as if it's in its own 'users' app.
        """
        custom_app_label = "users"

    # LIST DISPLAY
    @admin.display(description="First name")
    def get_first_name(self, obj: models.Profile) -> str:
        """
        Manual extraction of the associated user's first_name, since user__first_name is disallowed in list_display
        for some reason.
        """
        return obj.user.first_name

    @admin.display(description="Surname")
    def get_last_name(self, obj: models.Profile) -> str:
        """
        Manual extraction of the associated user's last_name, since user__last_name is disallowed in list_display
        for some reason.
        """
        return obj.user.last_name

    # ACTIONS
    @admin.action(description="Approve selected users")
    def approve_user_accounts(self, request: http.HttpRequest, queryset: models.ProfileQuerySet) -> None:
        """
        Action allowing a SCHOOL_ADMIN user to approve other school users.
        """
        del request
        queryset.mark_selected_users_as_approved()

    def get_actions(self, request: http.HttpRequest) -> dict:
        """
        Override the get actions method to change the delete_selected short description.
        """
        actions = super().get_actions(request=request)
        callback, name, _short_description = actions["delete_selected"]
        actions["delete_selected"] = (callback, name, "Delete selected users")
        return actions

    # PERMISSIONS
    def has_add_permission(self, request: http.HttpRequest) -> bool:
        """
        It does not make sense for the admin to be able to make Profile model instances.
        """
        return False
