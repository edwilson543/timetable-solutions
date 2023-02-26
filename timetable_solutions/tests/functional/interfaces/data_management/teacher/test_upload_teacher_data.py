"""Tests for the page allowing users to upload a csv file containing teacher data."""

# Standard library imports
from unittest import mock

# Third party imports
from webtest import Upload

# Local application imports
from data import models
from interfaces.constants import ExampleFile, UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.utils import get_csv_from_lists


class TestUploadTeacherData(TestClient):
    @mock.patch("django.contrib.messages.success")
    def test_valid_csv_file_gets_processed_to_db(
        self, mock_success_messages: mock.Mock()
    ):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Navigate to the upload page
        url = UrlName.TEACHER_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Upload some valid teacher data as a csv file
        csv_file = get_csv_from_lists(
            [
                ["teacher_id", "firstname", "surname", "title"],
                [1, "Test", "Testson", "Mrs"],
            ]
        )
        upload_file = Upload(filename="teachers.csv", content=csv_file.read())
        form = page.forms["upload-form"]
        form["csv_file"] = upload_file
        response = form.submit()

        # Check response ok
        assert response.status_code == 302
        assert response.location == UrlName.TEACHER_LIST.url()
        mock_success_messages.assert_called_once()

        # Check relevant db content created
        teachers = models.Teacher.objects.all()
        assert teachers.count() == 1
        teacher = teachers.get()
        assert teacher.teacher_id == 1
        assert teacher.firstname == "Test"
        assert teacher.surname == "Testson"
        assert teacher.title == "Mrs"

    @mock.patch("django.contrib.messages.error")
    def test_invalid_upload_rejected(self, mock_error_messages: mock.Mock()):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Navigate to the upload page
        url = UrlName.TEACHER_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Create some invalid teacher data (non-unique teacher id)
        form = page.forms["upload-form"]
        csv_file = get_csv_from_lists(
            [
                ["teacher_id", "firstname", "surname", "title"],
                [1, "Test", "Testson", "Mrs"],
                [1, "Test", "Testson", "Mrs"],
            ]
        )
        upload_file = Upload(filename="teachers.csv", content=csv_file.read())
        form["csv_file"] = upload_file
        response = form.submit()

        # Check response ok and context
        assert response.status_code == 200
        mock_error_messages.assert_called_once()

        # Check no db content created
        teachers = models.Teacher.objects.all()
        assert teachers.count() == 0
