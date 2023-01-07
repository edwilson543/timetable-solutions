"""
Module containing integration tests for the TimetableFileUploadProcessor
"""

# Standard library imports
import datetime as dt

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase


# Local application imports
from data import models
from domain import data_upload_processing
from tests.input_settings import TEST_DATA_DIR


class TestTimetableSlotFileUploadProcessor(TestCase):
    """
    Test for timetable slot file uploads, which needs the YearGroup database table populated.
    """

    fixtures = ["user_school_profile.json", "year_groups.json"]
    valid_uploads = TEST_DATA_DIR / "valid_uploads"
    invalid_uploads = TEST_DATA_DIR / "invalid_uploads"

    def test_upload_timetable_structure_to_database_valid_upload(self):
        """
        Test that the TimetableSlotFileUploadProcessor can upload the
        timetable csv file and use it to populate database.
        """
        # Set test parameters
        with open(self.valid_uploads / "timetable.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.TimetableSlotFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 35)

        # Test that the database is as expected
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_slots.count(), 35)

        # Check a random individual slot
        slot = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=1
        )
        self.assertEqual(slot.day_of_week, 1)
        self.assertEqual(slot.period_starts_at, dt.time(hour=9))
        self.assertEqual(slot.period_duration, dt.timedelta(hours=1))

        # Check that all timetable slots have been associated with the correct year groups
        expected_year_groups = models.YearGroup.objects.get_specific_year_groups(
            school_id=123456, year_groups={"1", "2"}
        )
        for slot in all_slots:
            self.assertQuerysetEqual(
                slot.relevant_year_groups.all(), expected_year_groups
            )

    def test_upload_timetable_with_exciting_year_group_column_successful(self):
        """
        Test for uploading the timetable file when there are lots of combinations of
        raw relevant_year_group strings in the upload file.
        """
        # Set test parameters
        with open(self.valid_uploads / "timetable-mixed-ygs.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.TimetableSlotFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Test the upload was successful
        self.assertTrue(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 6)

        # Test that the database is as expected
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_slots.count(), 6)

        # Check year groups are as expected
        slot_1 = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=1
        )
        y_1 = models.YearGroup.objects.get_individual_year_group(
            school_id=123456, year_group="1"
        )
        self.assertEqual(slot_1.relevant_year_groups.all().first(), y_1)

        slot_2 = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=2
        )
        y_2 = models.YearGroup.objects.get_individual_year_group(
            school_id=123456, year_group="2"
        )
        self.assertEqual(slot_2.relevant_year_groups.all().first(), y_2)

        slot_3 = models.TimetableSlot.objects.get_individual_timeslot(
            school_id=123456, slot_id=3
        )
        reception = models.YearGroup.objects.get_individual_year_group(
            school_id=123456, year_group="Reception"
        )
        self.assertEqual(slot_3.relevant_year_groups.all().first(), reception)

        all_yg_slots = models.TimetableSlot.objects.get_specific_timeslots(
            school_id=123456, slot_ids={4, 6}
        )
        all_ygs = models.YearGroup.objects.get_all_instances_for_school(
            school_id=123456
        )
        for slot in all_yg_slots:
            self.assertQuerysetEqual(slot.relevant_year_groups.all(), all_ygs)

    def test_upload_timetable_with_empty_year_group_column_unsuccessful(self):
        """
        Users should receive an error message if their relevant_year_group column has a missing value
        """
        # Set test parameters
        with open(
            self.invalid_uploads / "timetable-missing-year-groups.csv", "rb"
        ) as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.TimetableSlotFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Test the upload was unsuccessful
        self.assertFalse(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 0)

        self.assertEqual(
            "No year groups were referenced in row 3!",
            upload_processor.upload_error_message,
        )

        # Test that the database is as expected
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_slots.count(), 0)

    def test_upload_timetable_referencing_invalid_year_group_unsuccessful(self):
        """
        Users should receive an error message if they try to refer to a non-existent year_group.
        """
        # Set test parameters
        with open(
            self.invalid_uploads / "timetable-invalid-year-group.csv", "rb"
        ) as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        # Upload the file
        upload_processor = data_upload_processing.TimetableSlotFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=123456,
        )

        # Test the upload was unsuccessful
        self.assertFalse(upload_processor.upload_successful)
        self.assertEqual(upload_processor.n_model_instances_created, 0)

        self.assertEqual(
            "Invalid year groups: 1;2;3 in row: 3. Please amend!",
            upload_processor.upload_error_message,
        )

        # Test that the database is as expected
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        self.assertEqual(all_slots.count(), 0)
