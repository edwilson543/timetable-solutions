# Third party imports
import pytest

# Django imports
from django.contrib.auth import models as auth_models

# Local application imports
from data import constants
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestRegistration(TestClient):
    """
    Tests for the end-to-end registration process.
    """

    def test_can_register_new_user_to_a_new_school(self):
        # Access the registration page
        register_url = UrlName.REGISTER.url()
        register_personal_details_step = self.client.get(url=register_url)

        # Registration Step 1: Fill out personal details
        personal_details_form = register_personal_details_step.forms["register-form"]

        personal_details_form["username"] = "dummy_teacher"
        personal_details_form["email"] = "dummy_teacher@dt.co.uk"
        personal_details_form["password1"] = "dt123dt123"
        personal_details_form["password2"] = "dt123dt123"
        personal_details_form["first_name"] = "dummy"
        personal_details_form["last_name"] = "teacher"

        pivot_step = personal_details_form.submit().follow()

        # Registration Step 2: State whether registering to a new or existing school
        pivot_form = pivot_step.forms["register-pivot-form"]
        pivot_form["existing_school"] = "NEW"

        register_school_details_step = pivot_form.submit().follow()

        # Registration Step 3a: Register the new school
        register_school_form = register_school_details_step.forms[
            "register-school-form"
        ]
        register_school_form["school_name"] = "My school"

        dashboard = register_school_form.submit()

        # Registration is now complete, so we now check for a successful outcome
        assert dashboard.status_code == 302
        assert dashboard.location == UrlName.DASHBOARD.url()

        user = auth_models.User.objects.get()
        assert user.username == "dummy_teacher"

        profile = user.profile
        assert profile.approved_by_school_admin

        school = profile.school
        assert school.school_name == "My school"

    @pytest.mark.parametrize(
        "position", [constants.UserRole.PUPIL.value, constants.UserRole.TEACHER.value]
    )
    def test_can_register_new_user_to_an_existing_school(self, position: str):
        # Make a school to register the new users to
        school = data_factories.School()

        # Access the registration page
        register_url = UrlName.REGISTER.url()
        register_personal_details_step = self.client.get(url=register_url)

        # Registration Step 1: Fill out personal details
        personal_details_form = register_personal_details_step.forms["register-form"]

        personal_details_form["username"] = "dummy_teacher"
        personal_details_form["email"] = "dummy_teacher@dt.co.uk"
        personal_details_form["password1"] = "dt123dt123"
        personal_details_form["password2"] = "dt123dt123"
        personal_details_form["first_name"] = "dummy"
        personal_details_form["last_name"] = "teacher"

        pivot_step = personal_details_form.submit().follow()

        # Registration Step 2: State whether registering to a new or existing school
        pivot_form = pivot_step.forms["register-pivot-form"]
        pivot_form["existing_school"] = "EXISTING"

        register_school_details_step = pivot_form.submit().follow()

        # Registration Step 3b: Register the new user to the existing school
        register_profile_form = register_school_details_step.forms[
            "register-profile-form"
        ]
        register_profile_form["school_access_key"] = school.school_access_key
        register_profile_form["position"] = position

        # The user is redirected to login while waiting for approval by their school admin
        back_to_login = register_profile_form.submit()

        # Registration is now complete, so we now check for a successful outcome
        assert back_to_login.status_code == 302
        assert back_to_login.location == UrlName.LOGIN.url()

        user = auth_models.User.objects.get()
        assert user.username == "dummy_teacher"

        profile = user.profile
        assert not profile.approved_by_school_admin
        assert profile.role == position

        assert profile.school == school

    def test_different_passwords_at_first_step_of_registration_process_causes_error(
        self,
    ):
        # Access the registration page
        register_url = UrlName.REGISTER.url()
        register_personal_details_step = self.client.get(url=register_url)

        # Registration Step 1: Fill out personal details, with 2 passwords that don't match
        personal_details_form = register_personal_details_step.forms["register-form"]

        personal_details_form["username"] = "dummy_teacher"
        personal_details_form["email"] = "dummy_teacher@dt.co.uk"
        personal_details_form["password1"] = "some password"
        personal_details_form["password2"] = "some other password"
        personal_details_form["first_name"] = "dummy"
        personal_details_form["last_name"] = "teacher"

        response = personal_details_form.submit()

        # Ensure the attempt was unsuccessful, in particular no user was created
        assert response.status_code == 200
        assert response.context["form"].errors.as_text()

        assert not auth_models.User.objects.exists()

    def test_invalid_access_key_at_final_stage_of_registration_process_causes_error(
        self,
    ):
        # Access the registration page
        register_url = UrlName.REGISTER.url()
        register_personal_details_step = self.client.get(url=register_url)

        # Registration Step 1: Fill out personal details
        personal_details_form = register_personal_details_step.forms["register-form"]

        personal_details_form["username"] = "dummy_teacher"
        personal_details_form["email"] = "dummy_teacher@dt.co.uk"
        personal_details_form["password1"] = "dt123dt123"
        personal_details_form["password2"] = "dt123dt123"
        personal_details_form["first_name"] = "dummy"
        personal_details_form["last_name"] = "teacher"

        pivot_step = personal_details_form.submit().follow()

        # Registration Step 2: State whether registering to a new or existing school
        pivot_form = pivot_step.forms["register-pivot-form"]
        pivot_form["existing_school"] = "EXISTING"

        register_school_details_step = pivot_form.submit().follow()

        # Registration Step 3b: Try registering the new user to a non-existent school
        register_profile_form = register_school_details_step.forms[
            "register-profile-form"
        ]
        register_profile_form["school_access_key"] = 1  # No corresponding school exists
        register_profile_form["position"] = constants.UserRole.PUPIL.value

        response = register_profile_form.submit()

        # Ensure no profile for the user was created
        assert response.status_code == 200
        assert response.context["form"].errors

        user = auth_models.User.objects.get()
        assert user.username == "dummy_teacher"

        assert not hasattr(user, "profile")
