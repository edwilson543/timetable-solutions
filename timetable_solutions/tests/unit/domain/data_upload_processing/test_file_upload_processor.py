"""
Module containing unit tests for the FileUploadProcessor
"""

# Third party imports
import pandas as pd

# Django imports
from django import test

# Local application imports
from data import models
from domain.data_upload_processing import FileUploadProcessor


class TestFileUploadProcessor(test.TestCase):
    """
    Unit test class for the methods on FileUploadProcessor.
    """
    fixtures = ["user_school_profile.json", "pupils.json", "timetable.json"]

    @staticmethod
    def _get_file_agnostic_processor() -> FileUploadProcessor:
        """
        Fixture for a FileUploadProcessor that is not specific to any of the upload files.
        """
        # noinspection PyTypeChecker
        processor = FileUploadProcessor(
            csv_file=None, csv_headers=None, id_column_name=None, model=None,  # None of these are relevant
            school_access_key=123456, attempt_upload=False,
        )
        return processor

    # TESTS FOR METHODS GETTING PUPILS / TIMETABLE SLOTS FORM STRING
    def test_get_pupils_from_raw_pupil_ids_string_valid(self):
        """
        Test that when the pupil_ids_raw kwarg is a valid string representing a list of pupils, a queryset
        of Pupils is returned as expected.
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()

        raw_string = "1, 4, 6"  # Bog standard string we know should work

        # Execute test unit
        pupils = processor._get_pupils_from_raw_pupil_ids_string(pupil_ids_raw=raw_string, row_number=1)

        # Check outcomes
        assert isinstance(pupils, models.PupilQuerySet)
        assert {pupil.pupil_id for pupil in pupils} == {1, 4, 6}

    def test_get_pupils_from_raw_pupil_ids_string_missing_pupils(self):
        """
        Test that when a string contains a pupil id without a corresponding Pupil, an error message is set
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()

        raw_string = "1, 4, 1000000, 333"   # Note that pupil with ids 1000000 333 does not exist for school 123456

        # Execute test unit
        pupils = processor._get_pupils_from_raw_pupil_ids_string(pupil_ids_raw=raw_string, row_number=1)

        # Check outcomes
        assert pupils is None
        assert "No pupil" in processor.upload_error_message
        assert ("1000000" in processor.upload_error_message) and ("333" in processor.upload_error_message)

    def test_get_timetable_slots_from_raw_slot_ids_string_valid(self):
        """
        Test that when the slot_ids_raw kwarg is a valid string representing a list of timetable slots, a queryset
        of TimetableSlots is returned as expected.
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()

        raw_string = "1, 2, 3"  # Bog standard string we know should work

        # Execute test unit
        slots = processor._get_timetable_slots_from_raw_slot_ids_string(slot_ids_raw=raw_string, row_number=1)

        # Check outcomes
        assert isinstance(slots, models.TimetableSlotQuerySet)
        assert {slot.slot_id for slot in slots} == {1, 2, 3}

    def test_get_timetable_slots_from_raw_slot_ids_string_missing_slots(self):
        """
        Test that when a string contains a slot id without a corresponding Timetableslot, an error message is set
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()

        raw_string = "1, 2, 123456, 412"   # Note that slots with ids 123456, 412 does not exist for school 123456

        # Execute test unit
        slots = processor._get_timetable_slots_from_raw_slot_ids_string(slot_ids_raw=raw_string, row_number=1)

        # Check outcomes
        assert slots is None
        assert "No timetable slot" in processor.upload_error_message
        assert ("123456" in processor.upload_error_message) and ("412" in processor.upload_error_message)

    def test_get_integer_set_from_string_valid_strings(self):
        """
        Test that the raw string cleaner is producing the correct set of integers
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()

        valid_strings = [
            "[1, 4, 6]", "1, 4, 6", "1; 4; 6", "1 & 4 & 6", "1, 4; 6 ", "[1 & 4 ; 6]"
            "[,1, 4, 6", "1, 4, 6]###!!!", "gets-remo, 1, 4, 6, ved ]", "6,,, 4, 1!!!!",
            "1       ,                4-, 6, ", "[][][1][][], 4[][ ][][, 6[][][][,,,,,,,,,][][][]",
            "vdwljhcbdwckw1cdwceqdeqdeq][dewqdkebkebd,4,***********\n\n\n\n\n,,,,,,,,new line??? random chars ,,,6"
        ]

        # Execute test unit (for each string, effectively redo the test)
        for valid_string in valid_strings:
            integer_set = processor._get_integer_set_from_string(raw_string_of_ids=valid_string, row_number=1)

            # Check outcome
            assert integer_set == {1, 4, 6}, f"{valid_string} caused test failure!"

    def test_get_integer_set_from_string_invalid_harmless_strings_return_none(self):
        """
        Test that the raw string cleaner is correctly handling strings that can signal an empty queryset
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()

        invalid_strings = [
            "", "[]", "[][][][][][]", "None", "N/A", "no slots / no pupils",
        ]

        # Execute test unit (for each string, effectively redo the test)
        for invalid_string in invalid_strings:
            integer_set = processor._get_integer_set_from_string(raw_string_of_ids=invalid_string, row_number=1)

            # Check outcome
            assert integer_set is None, f"{invalid_string} caused test failure!"

    # TESTS FOR STRING CLEANING ON INDIVIDUAL IDS
    def test_get_clean_id_from_file_field_value_unchanged_for_integers(self):
        """
        Test that when we pass an INTEGER id (the ideal format), it is unchanged by the cleaner.
        """
        # Set tst parameters
        raw_ids = [1, 10, 100, 123, 423412]
        processor = self._get_file_agnostic_processor()

        # Execute test unit
        for raw_id in raw_ids:
            cleaned_id = processor._get_clean_id_from_file_field_value(user_input_id=raw_id,
                                                                       row_number=1, field_name="irrelevant")

            # Check outcome
            assert cleaned_id == raw_id

    def test_get_clean_id_from_file_field_value_changed_for_floats(self):
        """
        Test that when we pass an FLOAT id the 0s don't get counted as factors of 10.
        """
        # Set tst parameters
        raw_ids = [1.0, 10.0, 100.0, 123.0, 423412.0]
        expected_converted_ids = [1, 10, 100, 123, 423412]
        processor = self._get_file_agnostic_processor()

        # Execute test unit
        for n, raw_id in enumerate(raw_ids):
            cleaned_id = processor._get_clean_id_from_file_field_value(user_input_id=raw_id,
                                                                       row_number=1, field_name="irrelevant")

            # Check outcome
            assert cleaned_id == expected_converted_ids[n]

    def test_get_clean_id_from_file_field_value_changed_for_strings(self):
        """
        Test that when we pass strings as IDs, they are handled in the appropriate way.
        """
        # Set tst parameters
        raw_ids = ["1.0", "10.0", "100", "123.0", "423412.0"]
        expected_converted_ids = [1, 10, 100, 123, 423412]
        processor = self._get_file_agnostic_processor()

        # Execute test unit
        for n, raw_id in enumerate(raw_ids):
            cleaned_id = processor._get_clean_id_from_file_field_value(user_input_id=raw_id,
                                                                       row_number=1, field_name="irrelevant")

            # Check outcome
            assert cleaned_id == expected_converted_ids[n]

    def test_get_clean_id_from_file_field_error_for_string_list(self):
        """
        Test that when we pass strings as IDs, they are handled in the appropriate way.
        """
        # Set tst parameters
        raw_id = "1, 2, 3"
        processor = self._get_file_agnostic_processor()

        # Execute test unit
        processor._get_clean_id_from_file_field_value(user_input_id=raw_id,
                                                      row_number=1, field_name="irrelevant")

        # Check outcome
        assert processor.upload_error_message is not None
        assert "Multiple" in processor.upload_error_message

    # TESTS FOR CHECKING UPLOAD FILE STRUCTURE AND CONTENT
    def test_check_upload_df_structure_and_content_no_data(self):
        """
        Unit test that an empty dataframe is not allowed but doesnt raise
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()
        df = pd.DataFrame({"test": []})

        # Execute test unit
        check_outcome = processor._check_upload_df_structure_and_content(upload_df=df)

        # Check outcome
        assert not check_outcome
        assert "No data" in processor.upload_error_message

    def test_check_upload_df_structure_and_content_headers_different_length(self):
        """
        Unit test that a dataframe with the wrong number of columns isn't allowed but doesn't raise
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()
        processor._csv_headers = ["a", "b", "c"]
        df = pd.DataFrame({"test": [1, 2, 3]})  # Note that the shape is wrong

        # Execute test unit
        check_outcome = processor._check_upload_df_structure_and_content(upload_df=df)

        # Check outcome
        assert not check_outcome
        assert "Input file headers" in processor.upload_error_message

    def test_check_upload_df_structure_and_content_headers_dont_match(self):
        """
        Unit test that a dataframe with the wrong column headers (but correct shape) isn't allowed but doesn't raise
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()
        processor._csv_headers = ["a", "b"]
        df = pd.DataFrame({"c": [1, 2, 3], "d": [4, 5, 6]})  # Note that shape is right but column names wrong

        # Execute test unit
        check_outcome = processor._check_upload_df_structure_and_content(upload_df=df)

        # Check outcome
        assert not check_outcome
        assert "Input file headers" in processor.upload_error_message

    def test_check_upload_df_structure_and_content_with_non_unique_id_column(self):
        """
        Unit test that a dataframe with the wrong column headers (but correct shape) isn't allowed but doesn't raise
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()
        processor._csv_headers = ["a", "b"]
        processor._id_column_name = "a"
        df = pd.DataFrame({"a": [1, 1, 2], "b": [4, 5, 6]})  # Note that column 'a' is the id column, but is not unique

        # Execute test unit
        check_outcome = processor._check_upload_df_structure_and_content(upload_df=df)

        # Check outcome
        assert not check_outcome
        assert "repeated ids" in processor.upload_error_message
