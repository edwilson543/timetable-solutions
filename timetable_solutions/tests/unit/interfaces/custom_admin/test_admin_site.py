"""
Unit tests for the user-orientated custom admin site
"""

# Django imports
from django import http
from django import test
from django import urls
from django.contrib.auth.models import User

# Local application imports
from constants.url_names import UrlName
from interfaces.custom_admin import admin


class TestCustomAdminSite(test.TestCase):

    fixtures = ["user_school_profile.json"]

    @staticmethod
    def get_request_from_school_admin() -> http.HttpRequest:
        """
        Utility method for producing a HTTP request from a permitted user.
        """
        factory = test.RequestFactory()
        request = factory.get(urls.reverse(UrlName.CREATE_TIMETABLES.value))
        request.user = User.objects.get(pk=1)  # Dummy teacher has pk=1
        return request

    def test_school_admin_user_can_access_site(self):
        """
        Test that a user with the role of 'SCHOOL_ADMIN' can access the custom admin site.
        """
        # Set test parameters
        request = self.get_request_from_school_admin()
        admin_site = admin.CustomAdminSite()

        # Execute test unit
        has_permission = admin_site.has_permission(request=request)

        # Check outcome
        assert has_permission

    def test_get_app_list(self):
        """
        Tests that the 'data' app which contains all project models is listed in the custom admin
        site app list
        """
        # Set test parameters
        request = self.get_request_from_school_admin()
        admin_site = admin.user_admin  # This has the ModelAdmins registered to it

        # Execute test unit
        app_list = admin_site.get_app_list(request=request)

        # Check outcome
        app_names = [app["name"] for app in app_list]
        assert app_names == ["Data"]

        model_names = {model["object_name"] for app in app_list for model in app["models"]}
        assert model_names == {"Pupil", "Teacher", "Classroom", "TimetableSlot", "Lesson"}
