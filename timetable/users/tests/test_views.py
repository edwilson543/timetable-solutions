# Django imports
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# Local application imports
from ..forms import CustomUserCreationForm, ProfileRegistrationForm, SchoolRegistrationForm
from ..models import School


class TestRegistration(TestCase):
    """Tests for the Register view class"""
    fixtures = ["users.json"]

    # REGISTRATION TESTS
    def test_register_new_user_valid_credentials(self):
        """We test that successful registration redirects to the correct url at the next stage of registration"""
        url = reverse('register')
        form_data = {"username": "dummy_teacher2", "email": "dummy_teacher@dt.co.uk",
                     "password1": "dt123dt123", "password2": "dt123dt123",
                     "first_name": "dummy", "last_name": "teacher"}
        response = self.client.post(url, data=form_data)
        self.assertIsNotNone(User.objects.get(username="dummy_teacher2"))
        self.assertEqual(User.objects.get(username="dummy_teacher2").first_name, "dummy")
        self.assertEqual(User.objects.get(username="dummy_teacher2").last_name, "teacher")
        self.assertRedirects(response, reverse("registration_pivot"))

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

    # PIVOT TESTS
    def test_register_school_pivot_towards_profile_registration(self):
        """
        If the user is part of an existing school, they should be redirected to enter profile details (i.e. associate
        themselves with the relevant school)
        """
        self.login_dummy_user()
        url = reverse('registration_pivot')
        form_data = {"existing_school": "EXISTING"}
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse("profile_registration"))

    def test_register_school_pivot_towards_school_registration(self):
        """
        Test that stating they are not part of an existing school redirects user to register their school for first
        time
        """
        self.login_dummy_user()
        url = reverse("registration_pivot")
        form_data = {"existing_school": "NEW"}
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse("school_registration"))

    # SCHOOL REGISTRATION TESTS
    def test_register_new_school(self):
        """
        Test that a school can be registered via the relevant form, and the user then gets redirected to their
        dashboard.
        """
        self.login_dummy_user()
        url = reverse('school_registration')
        form_data = {"school_access_key": 654321, "school_name": "Fake School"}
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse("dashboard"))

        new_school = School.objects.get(school_access_key=654321)
        self.assertIsInstance(new_school, School)

    def test_register_new_school_access_key_not_6_digits(self):
        """Should return the same form with an error message that tells users access key is not 6 digits."""
        self.login_dummy_user()
        url = reverse('school_registration')
        form_data = {"school_access_key": 12345, "school_name": "Fake School"}
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.context["error_message"], "Access key is not 6 digits")
        self.assertEqual(response.context["form"], SchoolRegistrationForm)

    def test_register_new_school_access_key_already_taken(self):
        """Should return the same form with an error message that tells user access key is already taken."""
        self.login_dummy_user()
        url = reverse('school_registration')
        form_data = {"school_access_key": 123456, "school_name": "Fake School"}
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.context["error_message"], "School with this School access key already exists.")
        self.assertEqual(response.context["form"], SchoolRegistrationForm)

    def test_register_new_school_access_key_entered_as_string(self):
        """Should return the same form with an error message that tells user access key is already taken."""
        self.login_dummy_user()
        url = reverse('school_registration')
        form_data = {"school_access_key": "abcabc", "school_name": "Fake School"}
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.context["error_message"], "Enter a whole number.")
        self.assertEqual(response.context["form"], SchoolRegistrationForm)

    # PROFILE REGISTRATION TESTS
    def test_register_profile_with_existing_school(self):
        """Test that a user can register themselves to an existing school"""
        self.login_dummy_user()
        url = reverse("profile_registration")

        form_data = {"school_access_key": 123456}
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse("dashboard"))

        existing_school = School.objects.get(school_access_key=123456)  # From fixture
        new_user_school = User.objects.get(username="dummy_teacher2").profile.school
        self.assertEqual(existing_school, new_user_school)

    def test_register_profile_with_existing_school_access_key_not_found(self):
        """Should return empty form with an error message that tells user access key was not found."""
        self.login_dummy_user()
        url = reverse('profile_registration')
        form_data = {"school_access_key": 765432}
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.context["error_message"], "Access key not found, please try again")
        self.assertEqual(response.context["form"], ProfileRegistrationForm)
