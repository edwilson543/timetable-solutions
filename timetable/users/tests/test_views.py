# Django imports
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# Local application imports
from ..forms import SchoolRegistrationPivot, CustomUserCreationForm, ProfileRegistrationForm, SchoolRegistrationForm
from ..models import School


class TestRegistration(TestCase):
    """Tests for the Register view class"""
    fixtures = ["users.json"]

    def test_register_new_user_valid_credentials(self):
        """
        We test that the correct form is returned within the context of the HTTP response - the next stage of
        registration should be the the pivot form to access key / school registration.
        """
        url = reverse('register')
        form_data = {"username": "dummy_teacher2", "email": "dummy_teacher@dt.co.uk",
                     "password1": "dt123dt123", "password2": "dt123dt123"}
        response = self.client.post(url, data=form_data)
        response_form = response.context["form"]
        self.assertEqual(response_form, SchoolRegistrationPivot)

    def test_register_new_user_invalid_credentials_passwords_different(self):
        """Test that entering invalid credentials simply leads back to the registration form plus error messages"""
        url = reverse('register')
        form_data = {"username": "dummy_teacher2", "email": "dummy_teacher@dt.co.uk",
                     "password1": "DIFFERENT_TO_PW_2", "password2": "dt123dt123"}
        response = self.client.post(url, data=form_data)
        response_form = response.context["form"]
        self.assertEqual(response_form, CustomUserCreationForm)
        response_error_message = response.context["error_messages"]["password_mismatch"]
        self.assertIn("password", response_error_message)

    def login_dummy_user(self):
        """Method to login a user, so that they can reach the later stages of registration."""
        user = User.objects.create_user(username="dummy_teacher2", password="dt123dt123")
        self.client.login(username="dummy_teacher2", password="dt123dt123")

    def test_register_school_pivot_towards_new_school(self):
        """
        We test that the form to register the school is returned, when the user selects the relevant radiobutton at
        stage 2 of registration.
        """
        self.login_dummy_user()
        url = reverse('registration_pivot')
        form_data = {"existing_school": "EXISTING"}
        response = self.client.post(url, data=form_data)
        response_form = response.context["form"]

        self.assertEqual(response_form, ProfileRegistrationForm)

    def test_register_new_school(self):
        """
        Test that a school can be registered via the relevant form, and the user then gets redirected to their
        dashboard.
        """
        self.login_dummy_user()
        url = reverse('school_registration')
        form_data = {"school_access_key": 12345, "school_name": "Fake School"}
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, "/users/dashboard/")

        new_school = School.objects.get(school_access_key=12345)
        self.assertIsInstance(new_school, School)

    def test_register_new_school_access_key_already_taken(self):
        # TODO
        pass

    def test_register_school_pivot_towards_new_profile(self):
        """We test that the form to enter an existing school's access key is returned"""
        self.login_dummy_user()
        url = reverse('registration_pivot')
        form_data = {"existing_school": "NEW"}
        response = self.client.post(url, data=form_data)
        response_form = response.context["form"]
        self.assertEqual(response_form, SchoolRegistrationForm)

    def test_register_profile_with_existing_school(self):
        """Test that a user can register themselves to an existing school"""
        self.login_dummy_user()
        url = reverse("profile_registration")

        form_data = {"school_access_key": 123}
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, "/users/dashboard/")

        existing_school = School.objects.get(school_access_key=123)  # From fixture
        new_user_school = User.objects.get(username="dummy_teacher2").profile.school
        self.assertEqual(existing_school, new_user_school)
