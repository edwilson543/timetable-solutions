"""
Module containing unit tests for the LessonFileUploadProcessor
"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.upload_processors import LessonFileUploadProcessor
from tests import data_factories


def _get_file_processor(
    school: models.School | None = None,
) -> LessonFileUploadProcessor:
    """
    LessonFileUploadProcessor that is used throughout the tests.
    """
    if not school:
        school = data_factories.School()

    processor = LessonFileUploadProcessor(
        csv_file=None,
        school_access_key=school.school_access_key,
        attempt_upload=False,
    )
    return processor


@pytest.mark.django_db
class TestLessonFileUploadProcessorGetPupilsFromRawPupilIdsString:
    def test_get_pupils_from_valid_raw_pupil_ids_string(self):
        school = data_factories.School()

        # Create three pupils to reference the raw ids of
        factory_pupils = [data_factories.Pupil(school=school) for _ in range(0, 3)]
        raw_string = "; ".join(str(pupil.pupil_id) for pupil in factory_pupils)

        # Create some other pupil not expected to be included in the resulting queryset
        excluded = data_factories.Pupil(school=school)

        processor = _get_file_processor(school=school)

        # Try processing the string of ids to a pupil queryset
        pupils = processor._get_pupils_from_raw_pupil_ids_string(
            pupil_ids_raw=raw_string, row_number=1
        )

        # Ensure all pupils were retrieved
        assert pupils.count() == 3
        assert excluded not in pupils

    def test_errors_for_raw_pupil_ids_string_referencing_non_existent_pupil(self):
        # Create no pupils, so our raw string reference will be invalid
        processor = _get_file_processor()
        raw_string = "1"

        # Execute test unit
        pupils = processor._get_pupils_from_raw_pupil_ids_string(
            pupil_ids_raw=raw_string, row_number=1
        )

        # Check outcomes
        assert pupils is None
        assert "No pupil" in processor.upload_error_message


@pytest.mark.django_db
class TestLessonFileUploadProcessorGetTimetableSlotsFromRawSlotIdsString:
    def test_get_timetable_slots_from_raw_slot_ids_string_valid(self):
        school = data_factories.School()

        # Create three pupils to reference the raw ids of
        factory_slots = [
            data_factories.TimetableSlot(school=school) for _ in range(0, 3)
        ]
        raw_string = "; ".join(str(slot.slot_id) for slot in factory_slots)

        # Create some other pupil not expected to be included in the resulting queryset
        excluded = data_factories.TimetableSlot(school=school)

        processor = _get_file_processor(school=school)

        # Try processing the string of ids to a pupil queryset
        slots = processor._get_timetable_slots_from_raw_slot_ids_string(
            slot_ids_raw=raw_string, row_number=1
        )

        # Ensure all pupils were retrieved
        assert slots.count() == 3
        assert excluded not in slots

    def test_errors_when_raw_string_references_non_existent_slot(self):
        # Create no timetable slots, so our raw string reference will be invalid
        processor = _get_file_processor()
        raw_string = "1"

        # Execute test unit
        slots = processor._get_timetable_slots_from_raw_slot_ids_string(
            slot_ids_raw=raw_string, row_number=1
        )

        # Check outcomes
        assert slots is None
        assert "No timetable slot" in processor.upload_error_message
