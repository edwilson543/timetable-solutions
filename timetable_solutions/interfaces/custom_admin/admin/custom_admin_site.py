"""
Module for the AdminSite instance used to implement the custom AdminSite.
"""

# Django imports
from django.contrib import admin
from django import http

# Local application imports
from data import models


class CustomAdminSite(admin.AdminSite):
    """
    Implementation of the custom AdminSite that users will have access to, to manage their data.
    """

    # Text to put at the end of each page's <title>.
    site_title = "Timetable solutions site admin"

    # Text to put in each page's <h1>.
    site_header = "Timetable solutions administration"

    # Text to put at the top of the admin index page.
    index_title = ""

    def has_permission(self, request: http.HttpRequest) -> bool:
        """
        Users can access the site if their role is 'SCHOOL_ADMIN', which is given to the user registering their
        school for the first time, and this user can give the same privilege to other users.
        """
        if hasattr(request.user, "profile"):
            return request.user.is_active and (request.user.profile.role == models.UserRole.SCHOOL_ADMIN.value)
        else:
            return False


# An instance of the CustomAdminSite is created to register all ModelAdmins to
# Note the name given is used to namespace all attached urls when using reverse
user_admin = CustomAdminSite(name="user_admin")
