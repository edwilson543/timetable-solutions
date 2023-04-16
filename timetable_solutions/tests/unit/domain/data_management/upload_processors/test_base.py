"""
Module containing unit tests for the FileUploadProcessor
"""


# Third party imports
import pandas as pd

# Local application imports
from domain.data_management.constants import FileStructure
from domain.data_management.upload_processors._base import (
    BaseFileUploadProcessor,
    RelationalUploadProcessorMixin,
)


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


class TestM2MUploadProcessorMixinGetIntegerSetFromString:
    def test_get_id_set_from_string_valid_input_to_ints(self):
        """
        Test that the mm processor can convert a raw string of ids to a list of integers.
        """
        # Set test parameters
        raw_string = "1;2;3;4;5"
        processor = RelationalUploadProcessorMixin()

        # Execute test unit
        id_list = processor.get_integer_set_from_string(
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
        processor = RelationalUploadProcessorMixin()

        for raw_string in raw_strings:
            # Execute test unit
            id_list = processor.get_integer_set_from_string(
                raw_string_of_ids=raw_string,
                row_number=1,
            )

            # Check outcome
            assert id_list is None

    def test_get_integer_set_from_string_valid_strings(self):
        """
        Test that the raw string cleaner is producing the correct set of integers
        """
        # Set test parameters
        processor = RelationalUploadProcessorMixin()

        valid_strings = [
            "[1, 4, 6]",
            "1, 4, 6",
            "1; 4; 6",
            "1 & 4 & 6",
            "1, 4; 6 ",
            "[1 & 4 ; 6]" "[,1, 4, 6",
            "1, 4, 6]###!!!",
            "gets-remo, 1, 4, 6, ved ]",
            "6,,, 4, 1!!!!",
            "1       ,                4-, 6, ",
            "[][][1][][], 4[][ ][][, 6[][][][,,,,,,,,,][][][]",
            "vdwljhcbdwckw1cdwceqdeqdeq][dewqdkebkebd,4,***********\n\n\n\n\n,,,,,,,,new line??? random chars ,,,6",
        ]

        # Execute test unit (for each string, effectively redo the test)
        for valid_string in valid_strings:
            integer_set = processor.get_integer_set_from_string(
                raw_string_of_ids=valid_string, row_number=1
            )

            # Check outcome
            assert integer_set == {
                1,
                4,
                6,
            }, f"{valid_string} caused test failure with wrong integer set: {integer_set}"

    def test_get_integer_set_from_string_invalid_harmless_strings_return_none(self):
        """
        Test that the raw string cleaner is correctly handling strings that can signal an empty queryset
        """
        # Set test parameters
        processor = RelationalUploadProcessorMixin()

        invalid_strings = [
            "",
            "[]",
            "[][][][][][]",
            "None",
            "N/A",
            "no slots / no pupils",
        ]

        # Execute test unit (for each string, effectively redo the test)
        for invalid_string in invalid_strings:
            integer_set = processor.get_integer_set_from_string(
                raw_string_of_ids=invalid_string, row_number=1
            )

            # Check outcome
            assert integer_set is None, f"{invalid_string} caused test failure!"


class TestM2MUploadProcessorMixinGetCleanIdFromFileFieldValue:
    def test_get_clean_id_from_file_field_value_unchanged_for_integers(self):
        """
        Test that when we pass an INTEGER id (the ideal format), it is unchanged by the cleaner.
        """
        # Set tst parameters
        raw_ids = [1, 10, 100, 123, 423412]
        processor = RelationalUploadProcessorMixin()

        # Execute test unit
        for raw_id in raw_ids:
            cleaned_id = processor.get_clean_id_from_file_field_value(
                user_input_id=raw_id, row_number=1, field_name="irrelevant"
            )

            # Check outcome
            assert cleaned_id == raw_id

    def test_get_clean_id_from_file_field_value_changed_for_floats(self):
        """
        Test that when we pass an FLOAT id the 0s don't get counted as factors of 10.
        """
        # Set tst parameters
        raw_ids = [1.0, 10.0, 100.0, 123.0, 423412.0]
        expected_converted_ids = [1, 10, 100, 123, 423412]
        processor = RelationalUploadProcessorMixin()

        # Execute test unit
        for n, raw_id in enumerate(raw_ids):
            cleaned_id = processor.get_clean_id_from_file_field_value(
                user_input_id=raw_id, row_number=1, field_name="irrelevant"
            )

            # Check outcome
            assert cleaned_id == expected_converted_ids[n]

    def test_get_clean_id_from_file_field_value_changed_for_strings(self):
        """
        Test that when we pass strings as IDs, they are handled in the appropriate way.
        """
        # Set tst parameters
        raw_ids = ["1.0", "10.0", "100", "123.0", "423412.0"]
        expected_converted_ids = [1, 10, 100, 123, 423412]
        processor = RelationalUploadProcessorMixin()

        # Execute test unit
        for n, raw_id in enumerate(raw_ids):
            cleaned_id = processor.get_clean_id_from_file_field_value(
                user_input_id=raw_id, row_number=1, field_name="irrelevant"
            )

            # Check outcome
            assert cleaned_id == expected_converted_ids[n]

    def test_get_clean_id_from_file_field_error_for_string_list(self):
        """
        Test that when we pass strings as IDs, they are handled in the appropriate way.
        """
        # Set tst parameters
        raw_id = "1, 2, 3"
        processor = RelationalUploadProcessorMixin()

        # Execute test unit
        processor.get_clean_id_from_file_field_value(
            user_input_id=raw_id, row_number=1, field_name="irrelevant"
        )

        # Check outcome
        assert processor.upload_error_message is not None
        assert "Multiple" in processor.upload_error_message
