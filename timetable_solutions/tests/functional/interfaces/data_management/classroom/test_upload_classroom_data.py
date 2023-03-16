"""
Tests for the page allowing users to upload a csv file containing classroom data.
"""

# Standard library imports
from unittest import mock

# Third party imports
from webtest import Upload

# Local application imports
from data import models
from domain.data_management.constants import ExampleFile
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers.csv import get_csv_from_lists


class TestUploadClassroomData(TestClient):
    @mock.patch("django.contrib.messages.success")
    def test_valid_csv_file_gets_processed_to_db(
        self, mock_success_messages: mock.Mock
    ):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Navigate to the upload page
        url = UrlName.CLASSROOM_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Upload some valid classroom data as a csv file
        csv_file = get_csv_from_lists(
            [
                ["classroom_id", "building", "room_number"],
                [1, "Test building", 100],
            ]
        )
        upload_file = Upload(filename="classrooms.csv", content=csv_file.read())
        form = page.forms["upload-form"]
        form["csv_file"] = upload_file
        response = form.submit()

        # Check response ok
        assert response.status_code == 302
        assert response.location == UrlName.CLASSROOM_LIST.url()
        mock_success_messages.assert_called_once()

        # Check relevant db content created
        classrooms = models.Classroom.objects.all()
        assert classrooms.count() == 1
        classroom = classrooms.get()
        assert classroom.classroom_id == 1
        assert classroom.building == "Test building"
        assert classroom.room_number == 100

    @mock.patch("django.contrib.messages.error")
    def test_invalid_upload_rejected(self, mock_error_messages: mock.Mock):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Navigate to the upload page
        url = UrlName.CLASSROOM_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Create some invalid classroom data (non-unique classroom id)
        form = page.forms["upload-form"]
        csv_file = get_csv_from_lists(
            [
                ["classroom_id", "building", "room_number"],
                [1, "Test building", 100],
                [1, "Test building", 100],
            ]
        )
        upload_file = Upload(filename="classrooms.csv", content=csv_file.read())
        form["csv_file"] = upload_file
        response = form.submit()

        # Check response ok and context
        assert response.status_code == 200
        mock_error_messages.assert_called_once()

        # Check no db content created
        classrooms = models.Classroom.objects.all()
        assert classrooms.count() == 0

    def test_can_download_example_file_then_upload_it(self):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Navigate to the upload page
        url = UrlName.CLASSROOM_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Download the example file
        file_response = page.click(href=UrlName.CLASSROOM_DOWNLOAD.url())

        assert file_response.headers["Content-Type"] == "text/csv"
        assert (
            file_response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.CLASSROOMS.value}"'
        )

        # Re-upload the file
        file = Upload(filename="classrooms.csv", content=file_response.body)
        form = page.forms["upload-form"]
        form["csv_file"] = file
        upload_response = form.submit()

        # Check upload successful
        assert models.Classroom.objects.count() > 0
        assert upload_response.location == UrlName.CLASSROOM_LIST.url()
