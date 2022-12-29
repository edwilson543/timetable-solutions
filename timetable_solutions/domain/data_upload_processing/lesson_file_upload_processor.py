"""
Implementation for the special case of handling the Lesson file upload
"""

# Standard library imports
import ast
import re
from typing import Type

# Third party imports
import pandas as pd

# Django imports
from django.core.files.uploadedfile import UploadedFile

# Local application imports
from .constants import Header, UploadFileStructure
from .file_upload_processor import FileUploadProcessor
from data import models
from data.utils import ModelSubclass


class LessonFileUploadProcessor(FileUploadProcessor):
    """
    Processing class for the user's file upload defining Lesson data.
    This model is a 'special case' and hence gets its own class (due to the foreign keys and many-to-many fields,
    it must tbe uploaded last
    """

    def __init__(self,
                 school_access_key: int,
                 csv_file: UploadedFile,
                 csv_headers: list[str] = UploadFileStructure.LESSON.headers,
                 id_column_name: str = UploadFileStructure.LESSON.id_column,
                 model: Type[ModelSubclass] = models.Lesson,
                 attempt_upload: bool = True):
        super().__init__(school_access_key=school_access_key, csv_file=csv_file, csv_headers=csv_headers,
                         id_column_name=id_column_name, model=model, attempt_upload=attempt_upload)

    def _get_data_dict_from_row_for_create_new(self, row: pd.Series, row_number: int) -> dict:
        """
        Customisation of the base class' method fore extracting data from the row.
        The output is a dictionary which can be passed directly to the Lesson model's create_new method.
        """
        create_new_dict = super()._get_data_dict_from_row_for_create_new(row=row, row_number=row_number)

        if Header.TEACHER_ID in create_new_dict.keys():
            raw_teacher_id = create_new_dict.pop(Header.TEACHER_ID)
            create_new_dict[Header.TEACHER_ID] = self._get_clean_id_from_file_field_value(
                user_input_id=raw_teacher_id, row_number=row_number, field_name="teachers")

        if Header.CLASSROOM_ID in create_new_dict.keys():
            raw_classroom_id = create_new_dict.pop(Header.CLASSROOM_ID)
            create_new_dict[Header.CLASSROOM_ID] = self._get_clean_id_from_file_field_value(
                user_input_id=raw_classroom_id, row_number=row_number, field_name="classrooms")

        if Header.PUPIL_IDS in create_new_dict.keys():
            raw_pupil_ids = create_new_dict.pop(Header.PUPIL_IDS)
            create_new_dict[models.Lesson.Constant.pupils] = self._get_pupils_from_raw_pupil_ids_string(
                pupil_ids_raw=raw_pupil_ids, row_number=row_number)

        if Header.USER_DEFINED_SLOTS in create_new_dict.keys():
            raw_slot_ids = create_new_dict.pop(Header.USER_DEFINED_SLOTS)
            create_new_dict[
                models.Lesson.Constant.user_defined_time_slots] = self._get_timetable_slots_from_raw_slot_ids_string(
                slot_ids_raw=raw_slot_ids, row_number=row_number)

        create_new_dict_ = {key: value for key, value in create_new_dict.items() if value is not None}
        return create_new_dict

    # METHODS TO GET QUERY SETS FROM RAW STRINGS
    def _get_pupils_from_raw_pupil_ids_string(self, pupil_ids_raw: str,
                                              row_number: int) -> models.PupilQuerySet | None:
        """
        Method to retrieve a queryset of Pupils from a raw user-upload string.
        :return either a queryset of Pupils if pupil_ids_raw is in the correct format; otherwise None
        Note that nans / self.__nan_handler will NOT be passed to this method.
        """
        pupil_ids = self._get_integer_set_from_string(raw_string_of_ids=pupil_ids_raw, row_number=row_number)
        if pupil_ids is not None:
            pupils = models.Pupil.objects.get_specific_pupils(
                school_id=self._school_access_key, pupil_ids=pupil_ids)
            if pupils.count() < len(pupil_ids):
                missing_slots = set(pupil_ids) - {pupil.pupil_id for pupil in pupils}
                self.upload_error_message = f"No pupil(s) with ids: {missing_slots} were found!"
                return None
            else:
                return pupils
        return None

    def _get_timetable_slots_from_raw_slot_ids_string(self, slot_ids_raw: str,
                                                      row_number: int) -> models.TimetableSlotQuerySet | None:
        """
        Method to retrieve a queryset of TimetableSlots from a raw user-upload string.
        :return either a queryset of TimetableSlot if slot_ids_raw is in the correct format; otherwise None
        Note that nans / self.__nan_handler will NOT be passed to this method.
        """
        slot_ids = self._get_integer_set_from_string(raw_string_of_ids=slot_ids_raw, row_number=row_number)
        if slot_ids is not None:
            slots = models.TimetableSlot.objects.get_specific_timeslots(
                school_id=self._school_access_key, slot_ids=slot_ids)
            if slots.count() < len(slot_ids):
                missing_slots = set(slot_ids) - {slot.slot_id for slot in slots}
                self.upload_error_message = f"No timetable slot(s) with ids: {missing_slots} were found!"
                return None
            else:
                return slots
        return None

    # STRING CLEANING METHODS
    def _get_clean_id_from_file_field_value(self, user_input_id: str | int | float | None, row_number: int,
                                            field_name: str) -> int | None:
        """
        Method to clean a string the user has entered which should just be a single number (or None).
        We use _get_integer_set_from_string, and then return the single integer or None, in the case where the user
        has not given a valid value (which may not be an issue, since some id fields are nullable).
        """
        if user_input_id is not None:
            user_input_id = str(user_input_id)
            user_input_id_no_floats = re.sub(r"[.].+", "", user_input_id)  # User's id may be read-in as '10.0'
            id_set = self._get_integer_set_from_string(raw_string_of_ids=user_input_id_no_floats,
                                                       row_number=row_number)
            if id_set is not None:
                if len(id_set) > 1:
                    self.upload_error_message = f"Cannot currently have multiple {field_name} for a single class!\n" \
                                                f"Multiple ids were given in row: {row_number} - {user_input_id}"
                    return None
                else:
                    cleaned_id = next(iter(id_set))
                    return cleaned_id
        return None

    def _get_integer_set_from_string(self, raw_string_of_ids: str, row_number: int) -> set[int] | None:
        """
        Method to do some basic checks on a raw string that need to be evaluated as a python list, and try to evaluate
        it literally. The raw strings originate from user upload files.

        :return - a set of integers, or None in the case where there is an error.
        :side effects - to set the upload_error_message instance attribute, if an error is encountered.
        """
        # Clean up the string and make it into a list
        raw_string_of_ids = re.sub(r"[:;&-]", ",", raw_string_of_ids)  # standardise allowed join characters

        valid_chars = [",", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        raw_string_of_ids = "".join([character for character in raw_string_of_ids if character in valid_chars])
        raw_string_of_ids = re.sub(r",+", ",", raw_string_of_ids)
        if len(raw_string_of_ids) == 0 or raw_string_of_ids == ",":
            # This isn't an issue directly, so just return None here
            return None

        if raw_string_of_ids[0] == ",":
            raw_string_of_ids = raw_string_of_ids[1:]
        raw_string_of_ids = "[" + raw_string_of_ids
        raw_string_of_ids = raw_string_of_ids + "]"

        # Try to convert the string into a set of integers
        try:
            id_list = ast.literal_eval(raw_string_of_ids)
            unique_id_set = {int(value) for value in id_list}
            return unique_id_set

        except SyntaxError:
            error = f"Invalid syntax: {raw_string_of_ids} in row {row_number}! Please use the format: '1; 2; 3'"
            self.upload_error_message = error

        except ValueError:
            error = f"Could not interpret contents of: {row_number} as integers! Please use the format: '1; 2; 3;'"
            self.upload_error_message = error

        return None
