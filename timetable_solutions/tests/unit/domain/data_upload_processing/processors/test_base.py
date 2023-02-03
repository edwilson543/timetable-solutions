"""
Module containing unit tests for the FileUploadProcessor
"""

# Third party imports
import pandas as pd

# Local application imports
from domain.data_upload_processing.processors._base import (
    BaseFileUploadProcessor,
    RelationalUploadProcessorMixin,
)
from domain.data_upload_processing.constants import FileStructure


class TestBaseFileUploadProcessor:
    """
    Unit test class for the methods on FileUploadProcessor.
    """

    @staticmethod
    def _get_file_agnostic_processor() -> BaseFileUploadProcessor:
        """
        Fixture for a FileUploadProcessor that is not specific to any of the upload files.
        """
        # None of the parameters are relevant to these tests
        # noinspection PyTypeChecker
        processor = BaseFileUploadProcessor(
            csv_file=None,
            school_access_key=None,
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


class TestM2MUploadProcessorMixin:
    """
    Unit test class for the methods on M2MUploadProcessorMixin.
    """

    def test_get_id_set_from_string_valid_input_to_ints(self):
        """
        Test that the mm processor can convert a raw string of ids to a list of integers.
        """
        # Set test parameters
        raw_string = "1;2;3;4;5"

        # Execute test unit
        id_list = RelationalUploadProcessorMixin().get_integer_set_from_string(
            raw_string_of_ids=raw_string,
            row_number=1,
        )

        # Check outcome
        assert id_list == frozenset({1, 2, 3, 4, 5})

    def test_get_id_set_from_string_returns_none_from_invalid_input_to_ints(self):
        """
        Test that the mm processor can convert a raw string of ids to a list of integers.
        """
        # Set test parameters
        raw_strings = ["", ";", ",", "dwfvwdojfvbewfvjbwvew,,fewew,"]

        for raw_string in raw_strings:
            # Execute test unit
            id_list = RelationalUploadProcessorMixin().get_integer_set_from_string(
                raw_string_of_ids=raw_string,
                row_number=1,
            )

            # Check outcome
            assert id_list is None
