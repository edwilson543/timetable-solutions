"""Unit tests for generic data upload view of the data_upload app"""

# Django imports
from django.test import TestCase
from django.urls import reverse

# Local application imports
from constants.url_names import UrlName
from domain.data_upload_processing import UploadStatus
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
        # Set test parameters
        login = self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.get(url)

        # Check the outcome - that all forms are currently incomplete
        required_forms = response.context["required_forms"]
        disallowed_forms = ["unsolved_classes", "fixed_classes"]  # Will have status 'disallowed', not 'incomplete'
        for form_name, required_upload in required_forms.items():
            self.assertIsInstance(required_upload, RequiredUpload)
            self.assertIsInstance(required_upload.empty_form, FormSubclass)

            if form_name in disallowed_forms:
                self.assertEqual(required_upload.upload_status, UploadStatus.DISALLOWED.value)
            else:
                self.assertEqual(required_upload.upload_status, UploadStatus.INCOMPLETE.value)

    def test_upload_page_view_no_upload_post_request_correct_context(self):
        """
        Upload page view is called by all file upload view, which gathers all forms and their completion status
        A post request should return all the forms and their upload status, just as for the get request.
        """
        # Set test parameters
        login = self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check the outcome
        required_forms = response.context["required_forms"]
        disallowed_forms = ["unsolved_classes", "fixed_classes"]  # Will have status 'disallowed', not 'incomplete'
        for form_name, required_upload in required_forms.items():
            self.assertIsInstance(required_upload, RequiredUpload)
            self.assertIsInstance(required_upload.empty_form, FormSubclass)

            if form_name in disallowed_forms:
                self.assertEqual(required_upload.upload_status, UploadStatus.DISALLOWED.value)
            else:
                self.assertEqual(required_upload.upload_status, UploadStatus.INCOMPLETE.value)

    # Logged out user tests
    def test_upload_page_view_no_login_redirects_to_login_page(self):
        """
        Test that trying to access the data upload page redirects logged out users to the login page.
        """
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)
        response = self.client.get(url)
        self.assertIn("users/accounts/login", response.url)  # We don't assert equal due to 'next' redirect field name

    def test_post_request_no_login_to_a_file_upload_url_redirects_to_login_page(self):
        """
        Test that trying to post data (e.g. to the pupil url, equivalently for all other files) redirects logged out
        users to the login page.
        """
        url = reverse(UrlName.PUPIL_LIST_UPLOAD.value)
        response = self.client.post(url, data={"junk": "not-a-file"})
        self.assertIn("users/accounts/login", response.url)  # We don't assert equal due to 'next' redirect field name


class TestUploadPageReviewExistingUploads(TestCase):
    """Unit tests for the upload_page_view when some files have been uploaded."""

    fixtures = ["user_school_profile.json", "pupils.json", "teachers.json"]

    def test_upload_page_view_uploads_get_request_completion_statuses_match_loaded_fixtures(self):
        """
        Unit test that the completion statuses in the required forms dict is in line with the fixtures loaded in by
        this test class
        """
        # Set test parameters
        login = self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.get(url)

        # Test the outcome
        required_forms = response.context["required_forms"]
        for required_upload in required_forms.values():
            self.assertIsInstance(required_upload, RequiredUpload)
        self.assertEqual(required_forms["pupils"].upload_status, UploadStatus.COMPLETE.value)
        self.assertEqual(required_forms["teachers"].upload_status, UploadStatus.COMPLETE.value)
        self.assertEqual(required_forms["classrooms"].upload_status, UploadStatus.INCOMPLETE.value)
        self.assertEqual(required_forms["timetable"].upload_status, UploadStatus.INCOMPLETE.value)
        self.assertEqual(required_forms["fixed_classes"].upload_status, UploadStatus.DISALLOWED.value)
        self.assertEqual(required_forms["unsolved_classes"].upload_status, UploadStatus.DISALLOWED.value)