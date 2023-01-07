"""
Implementation for the special case of handling the Lesson file upload
"""

# Standard library imports
import re

# Third party imports
import pandas as pd

# Django imports
from django.core.files.uploadedfile import UploadedFile

# Local application imports
from domain.data_upload_processing.constants import Header, UploadFileStructure
from domain.data_upload_processing.processors.base_processors import (
    BaseFileUploadProcessor,
    M2MUploadProcessorMixin,
)
from data import models


class LessonFileUploadProcessor(BaseFileUploadProcessor, M2MUploadProcessorMixin):
    """
    Processing class for the user's file upload defining Lesson data.
    This model is a 'special case' and hence gets its own class (due to the foreign keys and many-to-many fields,
    it must tbe uploaded last
    """

    model = models.Lesson
    file_structure = UploadFileStructure.LESSON

    def __init__(
        self,
        school_access_key: int,
        csv_file: UploadedFile,
        attempt_upload: bool = True,
    ):
        super().__init__(
            school_access_key=school_access_key,
            csv_file=csv_file,
            attempt_upload=attempt_upload,
        )

    def _get_data_dict_from_row_for_create_new(
        self, row: pd.Series, row_number: int
    ) -> dict:
        """
        Customisation of the base class' method for extracting data from the row.
        The output is a dictionary which can be passed directly to the Lesson model's create_new method.
        """
        create_new_dict = super()._get_data_dict_from_row_for_create_new(
            row=row, row_number=row_number
        )

        if Header.TEACHER_ID in create_new_dict:
            raw_teacher_id = create_new_dict.pop(Header.TEACHER_ID)
            create_new_dict[
                Header.TEACHER_ID
            ] = self._get_clean_id_from_file_field_value(
                user_input_id=raw_teacher_id,
                row_number=row_number,
                field_name="teachers",
            )

        if Header.CLASSROOM_ID in create_new_dict:
            raw_classroom_id = create_new_dict.pop(Header.CLASSROOM_ID)
            create_new_dict[
                Header.CLASSROOM_ID
            ] = self._get_clean_id_from_file_field_value(
                user_input_id=raw_classroom_id,
                row_number=row_number,
                field_name="classrooms",
            )

        if Header.PUPIL_IDS in create_new_dict:
            raw_pupil_ids = create_new_dict.pop(Header.PUPIL_IDS)
            create_new_dict[
                models.Lesson.Constant.pupils
            ] = self._get_pupils_from_raw_pupil_ids_string(
                pupil_ids_raw=raw_pupil_ids, row_number=row_number
            )

        if Header.USER_DEFINED_SLOTS in create_new_dict:
            raw_slot_ids = create_new_dict.pop(Header.USER_DEFINED_SLOTS)
            create_new_dict[
                models.Lesson.Constant.user_defined_time_slots
            ] = self._get_timetable_slots_from_raw_slot_ids_string(
                slot_ids_raw=raw_slot_ids, row_number=row_number
            )

        create_new_dict_ = {
            key: value for key, value in create_new_dict.items() if value is not None
        }
        return create_new_dict_

    # METHODS TO GET QUERY SETS FROM RAW STRINGS
    def _get_pupils_from_raw_pupil_ids_string(
        self, pupil_ids_raw: str, row_number: int
    ) -> models.PupilQuerySet | None:
        """
        Method to retrieve a queryset of Pupils from a raw user-upload string.
        :return either a queryset of Pupils if pupil_ids_raw is in the correct format; otherwise None
        Note that nans / self.__nan_handler will NOT be passed to this method.
        """
        pupil_ids = self._get_integer_set_from_string(
            raw_string_of_ids=pupil_ids_raw, row_number=row_number
        )
        if pupil_ids is not None:
            pupils = models.Pupil.objects.get_specific_pupils(
                school_id=self._school_access_key, pupil_ids=pupil_ids
            )
            if pupils.count() < len(pupil_ids):
                missing_slots = set(pupil_ids) - {pupil.pupil_id for pupil in pupils}
                self.upload_error_message = (
                    f"No pupil(s) with ids: {missing_slots} were found!"
                )
                return None
            else:
                return pupils
        return None

    def _get_timetable_slots_from_raw_slot_ids_string(
        self, slot_ids_raw: str, row_number: int
    ) -> models.TimetableSlotQuerySet | None:
        """
        Method to retrieve a queryset of TimetableSlots from a raw user-upload string.
        :return either a queryset of TimetableSlot if slot_ids_raw is in the correct format; otherwise None
        Note that nans / self.__nan_handler will NOT be passed to this method.
        """
        slot_ids = self._get_integer_set_from_string(
            raw_string_of_ids=slot_ids_raw, row_number=row_number
        )
        if slot_ids is not None:
            slots = models.TimetableSlot.objects.get_specific_timeslots(
                school_id=self._school_access_key, slot_ids=slot_ids
            )
            if slots.count() < len(slot_ids):
                missing_slots = set(slot_ids) - {slot.slot_id for slot in slots}
                self.upload_error_message = (
                    f"No timetable slot(s) with ids: {missing_slots} were found!"
                )
                return None
            else:
                return slots
        return None

    # STRING CLEANING METHODS
    def _get_clean_id_from_file_field_value(
        self, user_input_id: str | int | float | None, row_number: int, field_name: str
    ) -> int | None:
        """
        Method to clean a string the user has entered which should just be a single number (or None).
        We use _get_integer_set_from_string, and then return the single integer or None, in the case where the user
        has not given a valid value (which may not be an issue, since some id fields are nullable).
        """
        if user_input_id is not None:
            user_input_id = str(user_input_id)
            user_input_id_no_floats = re.sub(
                r"[.].+", "", user_input_id  # User's id may be read-in as '10.0'
            )
            id_set = self._get_integer_set_from_string(
                raw_string_of_ids=user_input_id_no_floats,
                row_number=row_number,
            )
            if id_set is not None:
                if len(id_set) > 1:
                    self.upload_error_message = (
                        f"Cannot currently have multiple {field_name} for a single class!\n"
                        f"Multiple ids were given in row: {row_number} - {user_input_id}"
                    )
                    return None
                else:
                    cleaned_id = next(iter(id_set))
                    return cleaned_id
        return None

    def _get_integer_set_from_string(
        self,
        raw_string_of_ids: str,
        row_number: int,
    ) -> frozenset[int] | None:
        """
        Method providing a reduced entry point to M2MUploadProcessorMixin's get_id_set_from_string method,
        by only offering 2 of the arguments (which is what we always want for this processor.

        :return A set of ids, representing pupil ids or timetable slot ids.
        """
        return super().get_id_set_from_string(
            raw_string_of_ids=raw_string_of_ids,
            row_number=row_number,
            target_id_type=int,
            valid_id_chars=",0123456789",
        )
