"""
Unit tests for the user-orientated custom admin site
"""

# Third party imports
import pytest

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

    def test_get_urls(self):
        # Set test parameters
        admin_site = admin.user_admin  # This has the ModelAdmins registered to it

        # Execute test unit
        url_list = admin_site.get_urls()

        # Check outcome
        assert len(url_list) == 12

        url_namespace = "user_admin"
        with pytest.raises(urls.NoReverseMatch):
            urls.reverse(f"{url_namespace}:{UrlName.LOGIN.value}")
        with pytest.raises(urls.NoReverseMatch):
            urls.reverse(f"{url_namespace}:{UrlName.LOGOUT.value}")
        with pytest.raises(urls.NoReverseMatch):
            urls.reverse(f"{url_namespace}:{UrlName.PASSWORD_CHANGE.value}")
        with pytest.raises(urls.NoReverseMatch):
            urls.reverse(f"{url_namespace}:{UrlName.PASSWORD_CHANGE_DONE.value}")

    def test_get_app_list_correct(self):
        """
        Tests that the override of _build_app_dict results in the correct app_list for the site
        """
        # Set test parameters
        request = self.get_request_from_school_admin()
        admin_site = admin.user_admin  # This has the ModelAdmins registered to it

        # Execute test unit
        app_list = admin_site.get_app_list(request=request)

        # Check outcome
        app_names = [app["name"] for app in app_list]
        assert app_names == ["data", "users"]

        model_names = {model["object_name"] for app in app_list for model in app["models"]}
        assert model_names == {"Pupil", "Teacher", "Classroom", "TimetableSlot", "Lesson", "Profile"}

        # Url checks
        base_url = "/data/admin/data/"
        for app in app_list:
            assert app["app_url"] == base_url
            for model_data in app["models"]:
                assert base_url in model_data["admin_url"]
                if app["name"] == "data":
                    assert base_url in model_data["add_url"]
                elif app["name"] == "users":
                    assert model_data["add_url"] is None