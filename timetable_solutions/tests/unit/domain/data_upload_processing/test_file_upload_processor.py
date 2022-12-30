"""
Module containing unit tests for the FileUploadProcessor
"""

# Third party imports
import pandas as pd

# Django imports
from django import test

# Local application imports
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
            csv_file=None,
            csv_headers=None,
            id_column_name=None,
            model=None,  # None of these are relevant
            school_access_key=123456,
            attempt_upload=False,
        )
        return processor

    # TESTS FOR CHECKING UPLOAD FILE STRUCTURE AND CONTENT
    def test_check_upload_df_structure_and_content_no_data(self):
        """
        Unit test that an empty dataframe is not allowed but doesn't raise
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
        df = pd.DataFrame(
            {"c": [1, 2, 3], "d": [4, 5, 6]}
        )  # Note that shape is right but column names wrong

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
        df = pd.DataFrame(
            {"a": [1, 1, 2], "b": [4, 5, 6]}
        )  # Note that column 'a' is the id column, but is not unique

        # Execute test unit
        check_outcome = processor._check_upload_df_structure_and_content(upload_df=df)

        # Check outcome
        assert not check_outcome
        assert "repeated ids" in processor.upload_error_message
