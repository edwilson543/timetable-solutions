"""Unit tests for generic data upload view of the data_upload app"""

# Django imports
from django.test import TestCase
from django.urls import reverse

# Local application imports
from interfaces.data_upload.upload_view_base_class import RequiredUpload
from interfaces.data_upload.forms import FormSubclass


class TestUploadPageReviewNoUploads(TestCase):
    """Unit tests for the upload_page_view when no files have been uploaded."""

    fixtures = ["user_school_profile.json"]

    def test_upload_page_view_no_upload_get_request_correct_context(self):
        """
        Upload page view is called by all file upload view, which gathers all forms and their completion status.
        A get request should return all the forms and their upload status.
        """
        login = self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse("file_upload_page")
        response = self.client.get(url)

        # Test the context
        required_forms = response.context["required_forms"]
        for required_upload in required_forms.values():
            self.assertIsInstance(required_upload, RequiredUpload)
            self.assertEqual(required_upload.upload_status, "Incomplete")
            self.assertIsInstance(required_upload.empty_form, FormSubclass)

    def test_upload_page_view_no_upload_post_request_correct_context(self):
        """
        Upload page view is called by all file upload view, which gathers all forms and their completion status
        A post request should return all the forms and their upload status, just as for the get request.
        """
        login = self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse("file_upload_page")
        response = self.client.post(url)

        # Test the context
        required_forms = response.context["required_forms"]
        for required_upload in required_forms.values():
            self.assertIsInstance(required_upload, RequiredUpload)
            self.assertEqual(required_upload.upload_status, "Incomplete")
            self.assertIsInstance(required_upload.empty_form, FormSubclass)

    def test_upload_page_view_no_login_redirects_to_login_page(self):
        """Test that trying to access the data upload page redirects logged out users to the login page."""
        url = reverse("file_upload_page")
        response = self.client.get(url)
        self.assertIn("users/accounts/login", response.url)  # We don't assert equal due to 'next' redirect field name


class TestUploadPageReviewExistingUploads(TestCase):
    """Unit tests for the upload_page_view when some files have been uploaded."""

    fixtures = ["user_school_profile.json", "pupils.json", "teachers.json"]

    def test_upload_page_view_uploads_get_request_completion_statuses_correct(self):
        """Unit test that the pre-uploaded files are shown as complete"""
        login = self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse("file_upload_page")
        response = self.client.get(url)

        # Test the context
        required_forms = response.context["required_forms"]
        for required_upload in required_forms.values():
            self.assertIsInstance(required_upload, RequiredUpload)
        self.assertEqual(required_forms["pupils"].upload_status, "Complete")
        self.assertEqual(required_forms["teachers"].upload_status, "Complete")
        self.assertEqual(required_forms["fixed_classes"].upload_status, "Incomplete")
