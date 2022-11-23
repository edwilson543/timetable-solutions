"""
Base classes relevant to the custom admin site.
"""

# Django imports
from django.contrib import admin
from django import http

# Local application imports
from data import models


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base class which the ModelAdmin for each model inherits from.
    This class provides all major functionality for the custom admin site:
        - Permissions
        - Queryset filtering
    """

    # PERMISSIONS METHODS
    # ALL permissions require SCHOOL_ADMIN status, and so we just use the has_module_permission method above
    def has_module_permission(self, request: http.HttpRequest) -> bool:
        """
        Users with the role SCHOOL_ADMIN have module permissions
        """
        if hasattr(request.user, "profile"):
            return request.user.is_active and (request.user.profile.role == models.UserRole.SCHOOL_ADMIN.value)
        else:
            return False

    def has_add_permission(self, request: http.HttpRequest) -> bool:
        return self.has_module_permission(request=request)

    def has_view_permission(self, request: http.HttpRequest, obj=None) -> bool:
        return self.has_module_permission(request=request)

    def has_change_permission(self, request: http.HttpRequest, obj=None) -> bool:
        return self.has_module_permission(request=request)

    def has_delete_permission(self, request: http.HttpRequest, obj=None) -> bool:
        return self.has_module_permission(request=request)
