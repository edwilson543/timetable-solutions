# Django imports
from django.test import TestCase
from django.urls import reverse

# Local application imports
from ..forms import SchoolRegistrationPivot, CustomUserCreationForm


class TestRegistration(TestCase):
    """Tests for the Register view class"""

    def test_register_new_user_valid_credentials(self):
        """We test that the correct form is returned within the context of the HTTP response - the next stage of
         registration should be the the pivot form to access key / school registration."""
        url = reverse('register')
        form_data = {"username": "dummy_teacher", "email": "dummy_teacher@dt.co.uk",
                     "password1": "dt123dt123", "password2": "dt123dt123"}
        response = self.client.post(url, data=form_data)
        response_form = response.context["form"]
        self.assertEqual(response_form, SchoolRegistrationPivot)

    def test_register_new_user_invalid_credentials_passwords_different(self):
        """Test that entering invalid credentials simply leads back to the registration form plus error messages"""
        url = reverse('register')
        form_data = {"username": "dummy_teacher", "email": "dummy_teacher@dt.co.uk",
                     "password1": "DIFFERENT_TO_PW_2", "password2": "dt123dt123"}
        response = self.client.post(url, data=form_data)
        response = self.client.post(url, data=form_data)
        response_form = response.context["form"]
        self.assertEqual(response_form, CustomUserCreationForm)
        response_error_message = response.context["error_messages"]["password_mismatch"]
        self.assertIn("password", response_error_message)
