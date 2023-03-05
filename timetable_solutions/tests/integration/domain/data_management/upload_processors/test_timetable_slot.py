"""
Module containing integration tests for the TimetableFileUploadProcessor
"""


# Standard library imports
import copy
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile

# Local application imports
from data import constants as data_constants
from data import models
from domain.data_management import upload_processors
from domain.data_management.constants import Header
from tests import data_factories
from tests.helpers.csv import get_csv_from_lists


@pytest.mark.django_db
class TestTimetableSlotFileUploadProcessor:
    def test_two_slots_successful_and_processed_to_db(self):
        # Make some data that the csv file will need to reference
        school = data_factories.School()

        yg_1 = data_factories.YearGroup(school=school)
        yg_2 = data_factories.YearGroup(school=school)

        # Get a csv file-like object
        csv_file = get_csv_from_lists(
            [
                [
                    Header.SLOT_ID,
                    Header.DAY_OF_WEEK,
                    Header.STARTS_AT,
                    Header.ENDS_AT,
                    Header.RELEVANT_YEAR_GROUP_IDS,
                ],
                [
                    1,
                    data_constants.Day.MONDAY.value,
                    "09:00",
                    "10:00",
                    yg_1.year_group_id,
                ],
                [
                    2,
                    data_constants.Day.MONDAY.value,
                    "10:00",
                    "11:00",
                    f"{yg_1.year_group_id} & {yg_2.year_group_id}",
                ],
            ]
        )

        # Upload the file
        upload_file = SimpleUploadedFile("timetable.csv", csv_file.read())
        upload_processor = upload_processors.TimetableSlotFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Check basic outcome of upload
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 2

        # Check saved to db
        slots = models.TimetableSlot.objects.filter(school=school)
        assert slots.count() == 2

        # Check each TimetableSlot instance
        slot_1 = slots.get(slot_id=1)
        assert slot_1.day_of_week == data_constants.Day.MONDAY
        assert slot_1.starts_at == dt.time(hour=9)
        assert slot_1.ends_at == dt.time(hour=10)
        ygs = slot_1.relevant_year_groups.all()
        assert ygs.count() == 1 and ygs.first() == yg_1

        slot_2 = slots.get(slot_id=2)
        assert slot_2.day_of_week == data_constants.Day.MONDAY
        assert slot_2.starts_at == dt.time(hour=10)
        assert slot_2.ends_at == dt.time(hour=11)
        ygs = slot_2.relevant_year_groups.all()
        assert ygs.count() == 2 and (yg_1 in ygs) and (yg_2 in ygs)

    @pytest.mark.parametrize("missing_column_index", [0, 1, 2, 3, 4])
    def test_two_file_with_missing_column_unsuccessful(self, missing_column_index: int):
        # Make some data that the csv file will need to reference
        school = data_factories.School()

        yg = data_factories.YearGroup(school=school)

        valid_row = [
            1,
            data_constants.Day.MONDAY.value,
            "09:00",
            "10:00",
            yg.year_group_id,
        ]
        invalid_row = copy.copy(valid_row)
        invalid_row[missing_column_index] = None

        # Get a csv file-like object
        csv_file = get_csv_from_lists(
            [
                [
                    Header.SLOT_ID,
                    Header.DAY_OF_WEEK,
                    Header.STARTS_AT,
                    Header.ENDS_AT,
                    Header.RELEVANT_YEAR_GROUP_IDS,
                ],
                valid_row,
                invalid_row,
            ]
        )

        # Upload the file
        upload_file = SimpleUploadedFile("timetable.csv", csv_file.read())
        upload_processor = upload_processors.TimetableSlotFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Check basic outcome of upload
        assert not upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 0
        assert upload_processor.upload_error_message is not None

        # Check saved to db
        assert models.TimetableSlot.objects.filter(school=school).count() == 0

    def test_upload_timetable_referencing_invalid_year_group_unsuccessful(self):
        # Make some data that the csv file will need to reference (but intentionally no year group_
        school = data_factories.School()

        # Get a csv file-like object
        csv_file = get_csv_from_lists(
            [
                [
                    Header.SLOT_ID,
                    Header.DAY_OF_WEEK,
                    Header.STARTS_AT,
                    Header.ENDS_AT,
                    Header.RELEVANT_YEAR_GROUP_IDS,
                ],
                # Year group 10 is just some random number - not a valid id
                [1, data_constants.Day.MONDAY.value, "09:00", "10:00", 10],
            ]
        )

        # Upload the file
        upload_file = SimpleUploadedFile("timetable.csv", csv_file.read())
        upload_processor = upload_processors.TimetableSlotFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Check basic outcome of upload
        assert not upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 0
        assert "Invalid year groups" in upload_processor.upload_error_message

        # Check saved to db
        assert models.TimetableSlot.objects.filter(school=school).count() == 0
