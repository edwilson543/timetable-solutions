"""
Tests for the page allowing school admins to update users.
"""

# Local application imports
from data import constants
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestUpdateUserProfile(TestClient):
    def test_access_detail_page_with_disabled_form(self):
        # Make a user with a profile
        profile = data_factories.Profile(approved_by_school_admin=True)
        user = profile.user
        self.authorise_client_for_school(profile.school)

        # Navigate to this profile's detail view
        url = UrlName.USER_UPDATE.url(username=user.username)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        serialized_user_profile = page.context["serialized_model_instance"]
        assert serialized_user_profile["username"] == user.username
        assert serialized_user_profile["approved_by_school_admin"] == "Yes"

        # Check the initial form values match the year_group's
        form = page.forms["disabled-update-form"]
        assert form["first_name"].value == user.first_name
        assert form["last_name"].value == user.last_name
        assert form["approved_by_school_admin"].checked

    def test_hx_get_enables_form_then_can_approve_user(self):
        # Make a user with a profile
        profile = data_factories.Profile(approved_by_school_admin=False)
        user = profile.user
        self.authorise_client_for_school(profile.school)

        # Navigate to this profile's detail view
        url = UrlName.USER_UPDATE.url(username=user.username)
        form_partial = self.hx_get(url)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]

        # Fill in and post the form
        form["approved_by_school_admin"] = True

        response = form.submit(name="update-submit")

        # Check response ok and year_group details updated
        assert response.status_code == 302
        assert response.location == url

        profile.refresh_from_db()
        assert profile.approved_by_school_admin

    def test_cannot_access_user_details_if_not_a_school_admin(self):
        school = self.create_school_and_authorise_client(
            role=constants.UserRole.TEACHER
        )

        # Create a user to try and view the details of
        profile = data_factories.Profile(school=school)
        user = profile.user

        # Try accessing this user's update page
        url = UrlName.USER_UPDATE.url(username=user.username)
        self.client.get(url, status=403)

    def test_cannot_access_user_details_for_user_at_different_school(self):
        self.create_school_and_authorise_client()

        # Create a user for some different school
        other_school = data_factories.School()
        profile = data_factories.Profile(school=other_school)
        user = profile.user

        # Try accessing this user's update page from some other school
        url = UrlName.USER_UPDATE.url(username=user.username)
        self.client.get(url, status=403)
