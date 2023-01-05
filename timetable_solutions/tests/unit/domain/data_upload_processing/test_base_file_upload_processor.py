"""
Module containing unit tests for the FileUploadProcessor
"""

# Third party imports
import pandas as pd

# Django imports
from django import test

# Local application imports
from domain.data_upload_processing.base_file_upload_processor import (
    BaseFileUploadProcessor,
)
from domain.data_upload_processing.constants import FileStructure


class TestFileUploadProcessor(test.TestCase):
    """
    Unit test class for the methods on FileUploadProcessor.
    """

    fixtures = [
        "user_school_profile.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
    ]

    @staticmethod
    def _get_file_agnostic_processor() -> BaseFileUploadProcessor:
        """
        Fixture for a FileUploadProcessor that is not specific to any of the upload files.
        """
        # noinspection PyTypeChecker
        processor = BaseFileUploadProcessor(
            csv_file=None,  # Not relevant to these tests
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
        processor.file_structure = FileStructure(headers=["a", "b", "c"], id_column="")
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
        processor.file_structure = FileStructure(headers=["a", "b"], id_column="")
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
        processor.file_structure = FileStructure(headers=["a", "b"], id_column="a")
        df = pd.DataFrame(
            {"a": [1, 1, 2], "b": [4, 5, 6]}
        )  # Note that column 'a' is the id column, but is not unique

        # Execute test unit
        check_outcome = processor._check_upload_df_structure_and_content(upload_df=df)

        # Check outcome
        assert not check_outcome
        assert "repeated ids" in processor.upload_error_message
