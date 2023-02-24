"""Unit tests for generic data upload view of the data_upload app"""


# Django imports
from django import test
from django.contrib.auth.models import User
from django.urls import reverse

# Local application imports
from domain.data_management import UploadStatus
from interfaces.constants import UrlName
from interfaces.data_management import forms_legacy as forms
from interfaces.data_management.views import UploadPage
from interfaces.data_management.views.data_upload_page import RequiredUpload


class TestUploadPageView(test.TestCase):
    """
    Unit tests for the UploadPage TemplateView - the class-based view handling HTTP requests to the data upload page,
    when no files are uploaded.
    """

    fixtures = ["user_school_profile.json"]

    def test_get_context_data(self):
        """
        Test that the context data provided by the UploadPage view is as expected.
        Note we haven't loaded any fixtures beyond the basic user, and so all forms should be incomplete.
        """
        factory = test.RequestFactory()
        url = reverse(
            UrlName.FILE_UPLOAD_PAGE.value
        )  # This should be irrelevant to this test anyway
        request = factory.get(url)
        user = User.objects.get_by_natural_key(username="dummy_teacher")
        request.user = user
        upload_page = UploadPage(request=request)

        # Execute test unit
        context = upload_page.get_context_data()

        # Check outcome (a selection of it, at least)
        required_forms = context["required_forms"]
        for required_form in required_forms.values():
            assert isinstance(required_form, RequiredUpload)

        classrooms = required_forms["classrooms"]
        assert classrooms.form_name == "Classrooms"
        assert classrooms.upload_status.status == UploadStatus.INCOMPLETE
        assert isinstance(classrooms.empty_form, forms.ClassroomListUpload)
        assert classrooms.upload_url_name == UrlName.CLASSROOM_LIST_UPLOAD

        lessons = required_forms["lessons"]
        assert lessons.form_name == "Lessons"
        assert lessons.upload_status.status == UploadStatus.DISALLOWED
        assert isinstance(lessons.empty_form, forms.LessonUpload)
        assert lessons.upload_url_name == UrlName.LESSONS_UPLOAD

    def test_get_request_returns_correct_context(self):
        """
        A get request should return all the forms and their upload status.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.get(url)

        # Check the outcome - that all forms are currently incomplete
        required_forms = response.context["required_forms"]
        disallowed_forms = [  # Will have status 'disallowed', not 'incomplete'
            "pupils",
            "timetable",
            "lessons",
            "breaks",
        ]
        for form_name, required_upload in required_forms.items():
            self.assertIsInstance(required_upload, RequiredUpload)
            self.assertIsInstance(required_upload.empty_form, forms.UploadForm)

            if form_name in disallowed_forms:
                self.assertEqual(
                    required_upload.upload_status.status, UploadStatus.DISALLOWED
                )
            else:
                self.assertEqual(
                    required_upload.upload_status.status, UploadStatus.INCOMPLETE
                )

    def test_post_request_returns_correct_context(self):
        """
        UploadPage handles POST requests in the same way as GET requests, therefore we expect and identical outcome.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.post(url)

        # Check the outcome
        required_forms = response.context["required_forms"]
        disallowed_forms = [  # Will have status 'disallowed', not 'incomplete'
            "pupils",
            "timetable",
            "lessons",
            "breaks",
        ]
        for form_name, required_upload in required_forms.items():
            self.assertIsInstance(required_upload, RequiredUpload)
            self.assertIsInstance(required_upload.empty_form, forms.UploadForm)

            if form_name in disallowed_forms:
                self.assertEqual(
                    required_upload.upload_status.status, UploadStatus.DISALLOWED
                )
            else:
                self.assertEqual(
                    required_upload.upload_status.status, UploadStatus.INCOMPLETE
                )

    # Logged out user tests
    def test_get_request_with_no_login_redirects_to_login_page(self):
        """
        Test that trying to access the data upload page via a GET request redirects logged out users to the login page.
        """
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)
        response = self.client.get(url)
        self.assertIn(
            "users/accounts/login", response.url
        )  # We don't assert equal due to 'next' redirect field name

    def test_post_request_with_no_login_redirects_to_login_page(self):
        """
        Test that trying to POST to the data upload page just redirects logged out users to the login page.
        """
        url = reverse(UrlName.PUPIL_LIST_UPLOAD.value)
        response = self.client.post(url, data={"junk": "not-a-file"})
        self.assertIn(
            "users/accounts/login", response.url
        )  # We don't assert equal due to 'next' redirect field name


class TestUploadPageViewExistingUploads(test.TestCase):
    """Unit tests for the UploadPage when some files have been uploaded."""

    fixtures = ["user_school_profile.json", "teachers.json", "classrooms.json"]

    def test_upload_page_view_uploads_get_request_completion_statuses_match_loaded_fixtures(
        self,
    ):
        """
        Unit test that the completion statuses in the required forms dict is in line with the fixtures loaded in by
        this test class
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = reverse(UrlName.FILE_UPLOAD_PAGE.value)

        # Execute test unit
        response = self.client.get(url)

        # Test the outcome
        required_forms = response.context["required_forms"]
        for required_upload in required_forms.values():
            self.assertIsInstance(required_upload, RequiredUpload)

        self.assertEqual(
            required_forms["teachers"].upload_status.status, UploadStatus.COMPLETE
        )
        self.assertEqual(
            required_forms["classrooms"].upload_status.status, UploadStatus.COMPLETE
        )

        self.assertEqual(
            required_forms["year_groups"].upload_status.status, UploadStatus.INCOMPLETE
        )

        self.assertEqual(
            required_forms["pupils"].upload_status.status, UploadStatus.DISALLOWED
        )
        self.assertEqual(
            required_forms["timetable"].upload_status.status, UploadStatus.DISALLOWED
        )
        self.assertEqual(
            required_forms["lessons"].upload_status.status, UploadStatus.DISALLOWED
        )
