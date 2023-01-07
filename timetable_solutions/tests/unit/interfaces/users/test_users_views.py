"""
Unit tests for the views in the users app, which navigate login and registration.
"""

# Django imports
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# Local application imports
from constants.url_names import UrlName
from data import models
from interfaces.users import forms


class TestRegistration(TestCase):
    """Tests for the Register view class"""

    fixtures = ["user_school_profile.json"]

    # LOGIN TESTS
    def test_login_approved_user(self):
        """
        Test that a user whose credentials have been approved by the school admin can login successfully.
        """
        # Set test parameters
        url = reverse(UrlName.LOGIN.value)
        form_data = {"username": "dummy_teacher", "password": "dt123dt123"}

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertRedirects(response, expected_url=reverse(UrlName.DASHBOARD.value))

    def test_login_unapproved_user(self):
        """
        Test that a user whose credentials have NOT been approved by the school admin is not allowed to login, and is
        given the correct error message.
        """
        # Setup
        user = User.objects.create_user(
            username="dummy_teacher2", password="dt123dt123"
        )
        models.Profile.create_and_save_new(
            user=user,
            school_id=123456,
            role=models.UserRole.TEACHER.value,
            approved_by_school_admin=False,
        )  # This is the key bit

        # Set test parameters
        url = reverse(UrlName.LOGIN.value)
        form_data = {"username": "dummy_teacher2", "password": "dt123dt123"}

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        unapproved_error = response.context.get("unapproved_error")
        self.assertIn("not yet been approved", unapproved_error)
        self.assertTrue(user.is_authenticated)
        login_successful = response.wsgi_request.user.is_authenticated
        self.assertFalse(login_successful)

    # REGISTRATION TESTS
    def test_register_new_user_valid_credentials(self):
        """
        Test that successful registration redirects to the correct url at the next stage of registration
        """
        # Set test parameters
        url = reverse(UrlName.REGISTER.value)
        form_data = {
            "username": "dummy_teacher2",
            "email": "dummy_teacher@dt.co.uk",
            "password1": "dt123dt123",
            "password2": "dt123dt123",
            "first_name": "dummy",
            "last_name": "teacher",
        }

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertIsNotNone(User.objects.get(username="dummy_teacher2"))
        self.assertEqual(
            User.objects.get(username="dummy_teacher2").first_name, "dummy"
        )
        self.assertEqual(
            User.objects.get(username="dummy_teacher2").last_name, "teacher"
        )
        self.assertRedirects(response, reverse(UrlName.REGISTER_PIVOT.value))

    def test_register_new_user_invalid_credentials_passwords_different(self):
        """
        Test that entering invalid credentials simply leads back to the registration form plus error messages
        """
        # Set test parameters
        url = reverse(UrlName.REGISTER.value)
        form_data = {
            "username": "dummy_teacher2",
            "email": "dummy_teacher@dt.co.uk",
            "password1": "DIFFERENT_TO_PW_2",
            "password2": "dt123dt123",
        }

        # Execute test unit
        response = self.client.post(url, data=form_data)
        response_form = response.context["form"]

        # Check outcome
        self.assertEqual(response_form, forms.CustomUserCreation)
        response_error_message = response.context["error_messages"][0]
        self.assertIn("password", response_error_message)

    # PIVOT TESTS
    def login_dummy_user(self) -> None:
        """
        Helper method to login users, so that they can reach the later stages of registration.
        Side-effects - the test client's user becomes authenticated.
        """
        User.objects.create_user(username="dummy_teacher2", password="dt123dt123")
        self.client.login(username="dummy_teacher2", password="dt123dt123")

    def test_register_school_pivot_towards_profile_registration(self):
        """
        If the user is part of an existing school_id, they should be redirected to enter profile details (i.e. associate
        themselves with the relevant school_id)
        """
        # Set test parameters
        self.login_dummy_user()
        url = reverse(UrlName.REGISTER_PIVOT.value)
        form_data = {"existing_school": "EXISTING"}

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertRedirects(response, reverse(UrlName.PROFILE_REGISTRATION.value))

    def test_register_school_pivot_towards_school_registration(self):
        """
        Test that stating they are not part of an existing school_id redirects user to register their school_id for
        the first time
        """
        # Set test parameters
        self.login_dummy_user()
        url = reverse(UrlName.REGISTER_PIVOT.value)
        form_data = {"existing_school": "NEW"}

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertRedirects(response, reverse(UrlName.SCHOOL_REGISTRATION.value))

    # SCHOOL REGISTRATION TESTS
    def test_register_new_school(self):
        """
        Test that a school_id can be registered via the relevant form, and the user then gets redirected to their
        dashboard.
        """
        # Set test parameters
        self.login_dummy_user()
        url = reverse(UrlName.SCHOOL_REGISTRATION.value)
        form_data = {"school_name": "Fake School"}

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertRedirects(response, reverse(UrlName.DASHBOARD.value))

        # Check the user's profile has been correctly set
        profile = response.wsgi_request.user.profile
        user_school_id = profile.school.school_access_key
        self.assertEqual(
            user_school_id, 123457
        )  # Since 123456 is the max access key in the fixture
        self.assertEqual(profile.role, models.UserRole.SCHOOL_ADMIN)
        self.assertTrue(profile.approved_by_school_admin)

        # Check the flash message
        message = response.cookies["messages"].value
        self.assertIsInstance(message, str)

    # PROFILE REGISTRATION TESTS
    def test_register_profile_with_existing_school(self):
        """
        Test that a teacher can register themselves to an existing school_id
        """
        # Set test parameters
        self.login_dummy_user()
        url = reverse(UrlName.PROFILE_REGISTRATION.value)
        form_data = {
            "school_access_key": 123456,
            "position": models.UserRole.TEACHER.value,
        }

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertRedirects(response, reverse(UrlName.LOGIN.value))

        # Check the user's profile has been correctly set
        profile = response.wsgi_request.user.profile
        self.assertEqual(profile.school.school_access_key, 123456)
        self.assertEqual(profile.role, models.UserRole.TEACHER)
        self.assertFalse(profile.approved_by_school_admin)

        # Check the flash message
        message = response.cookies["messages"].value
        self.assertIsInstance(message, str)

    def test_register_profile_with_existing_school_access_key_not_found(self):
        """
        Should return empty form with an error message that tells user access key was not found.
        """
        # Set test parameters
        self.login_dummy_user()
        url = reverse(UrlName.PROFILE_REGISTRATION.value)
        form_data = {
            "school_access_key": 765432,
            "position": models.UserRole.PUPIL.value,
        }

        # Execute test unit
        response = self.client.post(url, data=form_data)

        # Check outcome
        self.assertEqual(
            response.context["error_message"], "Access key not found, please try again"
        )
        self.assertEqual(response.context["form"], forms.ProfileRegistration)
