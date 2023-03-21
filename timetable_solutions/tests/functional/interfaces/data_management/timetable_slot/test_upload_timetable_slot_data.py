"""
Tests for the page allowing users to upload a csv file containing slot data.
"""

# Standard library imports
import datetime as dt
from unittest import mock

# Third party imports
from webtest import Upload

# Local application imports
from data import constants, models
from domain.data_management.constants import ExampleFile
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers.csv import get_csv_from_lists


class TestUploadTimetableSlotData(TestClient):
    @mock.patch("django.contrib.messages.success")
    def test_valid_csv_file_gets_processed_to_db(
        self, mock_success_messages: mock.Mock
    ):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make some year groups to reference in the uploaded file
        yg_a = data_factories.YearGroup(school=school)
        yg_b = data_factories.YearGroup(school=school)
        # And one year group not to reference
        data_factories.YearGroup(school=school)

        # Navigate to the upload page
        url = UrlName.TIMETABLE_SLOT_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Upload some valid slot data as a csv file
        csv_file = get_csv_from_lists(
            [
                [
                    "slot_id",
                    "day_of_week",
                    "starts_at",
                    "ends_at",
                    "relevant_year_group_ids",
                ],
                [1, 1, "08:00", "08:45", f"{yg_a.year_group_id}; {yg_b.year_group_id}"],
            ]
        )
        upload_file = Upload(filename="slots.csv", content=csv_file.read())
        form = page.forms["upload-form"]
        form["csv_file"] = upload_file
        response = form.submit()

        # Check response ok
        assert response.status_code == 302
        assert response.location == UrlName.TIMETABLE_SLOT_LIST.url()
        mock_success_messages.assert_called_once()

        # Check relevant db content created
        slots = models.TimetableSlot.objects.all()
        assert slots.count() == 1
        slot = slots.get()
        assert slot.slot_id == 1
        assert slot.day_of_week == constants.Day.MONDAY
        assert slot.starts_at == dt.time(hour=8)
        assert slot.ends_at == dt.time(hour=8, minute=45)

        year_groups = slot.relevant_year_groups.all()
        assert year_groups.count() == 2
        assert yg_a in year_groups
        assert yg_b in year_groups

    @mock.patch("django.contrib.messages.error")
    def test_invalid_upload_rejected(self, mock_error_messages: mock.Mock):
        yg = data_factories.YearGroup()
        self.authorise_client_for_school(yg.school)

        # Navigate to the upload page
        url = UrlName.TIMETABLE_SLOT_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Create some invalid slot data (non-unique slot id)
        form = page.forms["upload-form"]
        csv_file = get_csv_from_lists(
            [
                ["slot_id", "firstname", "surname", "year_group_id"],
                [1, "Test", "Testson", yg.year_group_id],
                [1, "Test", "Testson", yg.year_group_id],
            ]
        )
        upload_file = Upload(filename="slots.csv", content=csv_file.read())
        form["csv_file"] = upload_file
        response = form.submit()

        # Check response ok and context
        assert response.status_code == 200
        mock_error_messages.assert_called_once()

        # Check no db content created
        slots = models.TimetableSlot.objects.all()
        assert slots.count() == 0

    def test_can_download_example_file_then_upload_it(self):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Set the year groups referenced in the upload file
        data_factories.YearGroup(school=school, year_group_id=1)
        data_factories.YearGroup(school=school, year_group_id=2)

        # Navigate to the upload page
        url = UrlName.TIMETABLE_SLOT_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Download the example file
        file_response = page.click(href=UrlName.TIMETABLE_SLOT_DOWNLOAD.url())

        assert file_response.headers["Content-Type"] == "text/csv"
        assert (
            file_response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.TIMETABLE.value}"'
        )

        # Re-upload the file
        file = Upload(filename="slots.csv", content=file_response.body)
        form = page.forms["upload-form"]
        form["csv_file"] = file
        upload_response = form.submit()

        # Check upload successful
        assert models.TimetableSlot.objects.count() > 0
        assert upload_response.location == UrlName.TIMETABLE_SLOT_LIST.url()
