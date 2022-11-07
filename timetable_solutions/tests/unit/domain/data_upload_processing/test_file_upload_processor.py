"""Module containing unit tests for the FileUploadProcessor"""

# Django imports
from django import test

# Local application imports
from data import models
from domain.data_upload_processing import FileUploadProcessor


class TestFileUploadProcessorFileAgnostic(test.TestCase):
    """
    Unit test class for the methods on the file upload processor that are file agnostic.
    """
    fixtures = ["user_school_profile.json", "pupils.json", "timetable.json"]

    @staticmethod
    def _get_file_agnostic_processor() -> FileUploadProcessor:
        """
        Fixture for a FileUploadProcessor that is not specific to any of the upload files.
        """
        # noinspection PyTypeChecker
        processor = FileUploadProcessor(
            csv_file=None, csv_headers=None, id_column_name=None, model=None, # None of these are relevant
            school_access_key=123456, attempt_upload=False,
        )
        return processor

    # TESTS FOR GETTING PUPILS / TIMETABLE SLOTS FROM ROW
    # TODO

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
        #TODO
        """
        # # Set test parameters - we effectively parameterise this test with the raw string list
        # processor = self._get_file_agnostic_processor()
        #
        # raw_string = "1, 4, 6"  # Bog standard string we know should work
        #
        # # Execute test unit
        # pupils = processor._get_pupils_from_raw_pupil_ids_string(pupil_ids_raw=raw_string, row_number=1)
        #
        # # Check outcomes
        # assert isinstance(pupils, models.PupilQuerySet)
        # assert {pupil.pupil_id for pupil in pupils} == {1, 4, 6}

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
        # TODO
        """
        # # Set test parameters
        # processor = self._get_file_agnostic_processor()
        #
        # raw_string = "1, 2, 3"  # Bog standard string we know should work
        #
        # # Execute test unit
        # slots = processor._get_timetable_slots_from_raw_slot_ids_string(slot_ids_raw=raw_string, row_number=1)
        #
        # # Check outcomes
        # assert isinstance(slots, models.TimetableSlotQuerySet)
        # assert {slot.slot_id for slot in slots} == {1, 2, 3}

    def test_get_integer_set_from_string_valid_strings(self):
        """
        Test that the raw string cleaner is producing the correct set of integers
        """
        # Set test parameters
        processor = self._get_file_agnostic_processor()

        valid_strings = [
            "[1, 4, 6]", "1, 4, 6", "[,1, 4, 6", "1, 4, 6]###!!!", "gets-remo, 1, 4, 6, ved ]", "6,,, 4, 1!!!!",
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
