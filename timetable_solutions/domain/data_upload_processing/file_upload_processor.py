"""Module containing utility class used to do the processing of the uploaded csv files into the database."""

# Standard library imports
import ast
from io import StringIO
import re
from typing import Dict, List, Set, Type

# Third party imports
import pandas as pd

# Django imports
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction, IntegrityError

# Local application imports
from data import models
from data.utils import ModelSubclass
from .constants import Header


class FileUploadProcessor:
    """
    Class for the processing unit which, following a POST request from the user involving a file upload, will take that
    file, check it fits the requirements, and then upload to the database or not as appropriate.
    """
    __nan_handler = "###ignorenan"  # Used to fill na values in uploaded file, since float (nan) is error-prone

    def __init__(self,
                 csv_file: UploadedFile,
                 csv_headers: List[str],
                 school_access_key: int,  # Unique identifier for the school_id which the data corresponds to
                 id_column_name: str,
                 model: Type[ModelSubclass],
                 is_unsolved_class_upload: bool = False,
                 is_fixed_class_upload: bool = False,
                 attempt_upload: bool = True):
        """
        :param csv_file: the file as received from the user upload
        :param csv_headers: the column headers from the csv file, which will correspond to the model fields
        :param id_column_name: string depending on whether the input file contains an id column
        :param model: the model that the file is used to create instances of

        :param is_unsolved_class_upload/is_fixed_class_upload - these represent special cases of the file upload
        process since the models the data are being uploaded to contain many-to-many relationships, and thus require
        their own methods (see _create_model_instance_from_row variations below)

        :param attempt_upload - whether to try to process the file's contents into the database.
        """
        # Instance attributes used internally
        self._csv_headers = csv_headers
        self._school_access_key = school_access_key
        self._id_column_name = id_column_name
        self._model = model
        self._is_unsolved_class_upload = is_unsolved_class_upload
        self._is_fixed_class_upload = is_fixed_class_upload

        # Instance attributes that get set during upload, providing info on the level of success
        self.n_model_instances_created = 0
        self.upload_error_message = None  # Provides details on why the upload has failed

        # Try uploading the file to the database
        if attempt_upload:
            self._upload_file_content(file=csv_file)

    def _upload_file_content(self, file: UploadedFile) -> None:
        """
        Method to attempt to save the file to the database.
        Note that we either want all rows to become model instances or none of them to, hence we use an atomic
        transaction once we have cleaned all the data.
        """
        file_extension = file.name.split(".")[1]
        if file_extension != "csv":
            self.upload_error_message = f"Please upload your file as with the .csv!\n" \
                                        f"File extension given was .{file_extension}."
            return

        try:
            file_bytes = file.read().decode("utf-8")
            file_stream = StringIO(file_bytes)
            # noinspection PyTypeChecker
            upload_df = pd.read_csv(file_stream, sep=",")
        except UnicodeDecodeError:
            self.upload_error_message = "Please check that your file is encoded using UTF-8!"
            return
        except pd.errors.ParserError:
            self.upload_error_message = "Bad file structure identified!\n" \
                                        "Please check that data is only given under the defined columns."
            return

        # Basic cleaning / checks on file content & structure
        upload_df.fillna(value=self.__nan_handler, inplace=True)
        upload_df.replace(to_replace="", value=self.__nan_handler)
        upload_df = self._convert_df_to_correct_types(upload_df)

        if not self._check_upload_df_structure_and_content(upload_df=upload_df):
            # Note that the error message attribute will be set as appropriate
            return

        # Process each file row into a dictionary to pass to create_new
        create_new_dict_list = self._get_data_dict_list_for_create_new(upload_df=upload_df)
        if self.upload_error_message is None:
            try:
                with transaction.atomic():
                    for n, create_new_dict in enumerate(create_new_dict_list):
                        self._model.create_new(**create_new_dict)

                # Reaching this point means the upload processing has been successful
                self.n_model_instances_created = len(create_new_dict_list)

            except (ValidationError,  # Model does not pass the full_clean checks
                    TypeError,  # Model was missing a required field (via its the create_new method)
                    ValueError):  # A string was passed to int(id_field)
                error = f"Could not interpret values in row {n+1} as a {self._model.Constant.human_string_singular}!" \
                            f"\nPlease check that all data is of the correct type and all ids referenced are in use!"
                self.upload_error_message = error
            except IntegrityError:
                error = f"ID given for {self._model.Constant.human_string_singular} in row {n + 1} was not unique!"
                self.upload_error_message = error

    def _get_data_dict_list_for_create_new(self, upload_df: pd.DataFrame) -> List[Dict] | None:
        """
        Method to iterate through the rows of the dataframe, and create a list of dictionaries that can be passed to
        self._model.create_new(**create_new_dict).
        """
        create_new_dict_list = []
        row_number = 1  # row_number is only used for user-targeted error messages, so count from 1 not 0

        for _, data_ser in upload_df.iterrows():

            # Get the dict
            if self._is_unsolved_class_upload:
                create_new_dict = self._get_data_dict_from_row_for_create_new_unsolved_class(
                    row=data_ser, row_number=row_number)
            elif self._is_fixed_class_upload:
                create_new_dict = self._get_data_dict_from_row_for_create_new_fixed_class(
                    row=data_ser, row_number=row_number)
            else:
                create_new_dict = self._get_data_dict_from_row_for_create_new_default(row=data_ser)

            # dict-getting methods will set errors, so if there is / isn't one set, proceed as appropriate
            if self.upload_error_message is None:
                create_new_dict_list.append(create_new_dict)
                row_number += 1
            else:
                # A single error means we write off the entire file contents
                return None

        return create_new_dict_list

    # METHODS CREATING DICTIONARIES TO BE PASSED TO self._model.create_new()
    def _get_data_dict_from_row_for_create_new_default(self, row: pd.Series) -> Dict[str, str | int]:
        """
        Method to take an individual row from the csv file, and convert it into a dictionary which can be passed
        directly to self._model.create_new(**create_new_dict) to initialise a model instance
        :return dictionary mapping create_new kwargs to the field values of self._model
        """
        initial_create_new_dict = row.to_dict()
        create_new_dict = {key: value for key, value in initial_create_new_dict.items() if value != self.__nan_handler}
        create_new_dict[Header.SCHOOL_ID] = self._school_access_key
        return create_new_dict

    def _get_data_dict_from_row_for_create_new_unsolved_class(self, row: pd.Series, row_number: int) -> Dict:
        """
        Method to process a single row of the unsolved class csv file upload (already converted to a Series).

        :param row - a single row from the uploaded file, indexed by the file headers. Note we already check the file
        has the correct headers, so don't need to worry about KeyErrors when indexing 'row'.
        :param row_number - the (1-based) number of the row we are processing. Only used for error messages.
        :return mapping of self._model.create_new method kwargs: kwarg values
        """
        initial_create_new_dict = self._get_data_dict_from_row_for_create_new_default(row=row)
        create_new_dict = {key: value for key, value in initial_create_new_dict.items() if value != self.__nan_handler}

        if Header.PUPIL_IDS in create_new_dict.keys():
            raw_pupil_ids = create_new_dict.pop(Header.PUPIL_IDS)
            create_new_dict[models.UnsolvedClass.Constant.pupils] = self._get_pupils_from_raw_pupil_ids_string(
                pupil_ids_raw=raw_pupil_ids, row_number=row_number)

        return create_new_dict

    def _get_data_dict_from_row_for_create_new_fixed_class(self, row: pd.Series, row_number: int) -> Dict:
        """
        Method to process a single row of the fixed class csv file upload (already converted to a Series).

        :param row - a single row from the uploaded file, indexed by the file headers. Note we already check the file
        has the correct headers, so don't need to worry about KeyErrors when indexing 'row'.
        :param row_number - the (1-based) number of the row we are processing. Only used for error messages.
        :return mapping of self._model.create_new method kwargs: kwarg values
        """
        initial_create_new_dict = self._get_data_dict_from_row_for_create_new_default(row=row)
        create_new_dict = {key: value for key, value in initial_create_new_dict.items() if value != self.__nan_handler}
        create_new_dict[models.FixedClass.Constant.user_defined] = True  # Not present in file, so manually add

        if Header.PUPIL_IDS in create_new_dict.keys():
            raw_pupil_ids = create_new_dict.pop(Header.PUPIL_IDS)
            create_new_dict[models.FixedClass.Constant.pupils] = self._get_pupils_from_raw_pupil_ids_string(
                pupil_ids_raw=raw_pupil_ids, row_number=row_number)

        if Header.SLOT_IDS in create_new_dict.keys():
            raw_slot_ids = create_new_dict.pop(Header.SLOT_IDS)
            create_new_dict[models.FixedClass.Constant.time_slots] = self._get_timetable_slots_from_raw_slot_ids_string(
                slot_ids_raw=raw_slot_ids, row_number=row_number)

        return create_new_dict

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

    def _get_integer_set_from_string(self, raw_string_of_ids: str, row_number: int) -> Set[int] | None:
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
        if len(raw_string_of_ids) == 0:
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

    # CHECKS ON UPLOAD FILE STRUCTURE
    def _check_upload_df_structure_and_content(self, upload_df: pd.DataFrame) -> bool:
        """
        Method to do an initial screening whether the user has uploaded a file with the correct headers.
        """
        # Check there is actually some data in the file
        if len(upload_df) == 0:
            self.upload_error_message = "No data was present in the uploaded file!"
            return False

        # Check that the file has the required column headers
        headers_error = "Input file headers did not match required format - please check against the example file."
        if len(upload_df.columns) == len(self._csv_headers):
            headers_valid = all(upload_df.columns == self._csv_headers)
            if not headers_valid:
                self.upload_error_message = headers_error
                return False
        else:
            self.upload_error_message = headers_error
            return False

        # Check that the id column contains no duplicates
        if self._id_column_name is not None:
            # This needs to be done upfront, as .validate_unique() called by .full_clean() is redundant here
            ids_unique = upload_df[self._id_column_name].is_unique
            if not ids_unique:
                self.upload_error_message = f"Input file contained repeated ids (id column is {self._id_column_name})"
                return False

        # All checks have passed so return True
        return True

    @staticmethod
    def _convert_df_to_correct_types(upload_df: pd.DataFrame) -> pd.DataFrame:
        """Method to ensure timestamps / timedelta are converted to the correct type"""
        if Header.PERIOD_DURATION in upload_df.columns:
            upload_df[Header.PERIOD_DURATION] = pd.to_timedelta(upload_df[Header.PERIOD_DURATION])
        if Header.PERIOD_STARTS_AT in upload_df.columns:
            upload_df[Header.PERIOD_STARTS_AT] = pd.to_datetime(upload_df[Header.PERIOD_STARTS_AT])
        return upload_df

    # PROPERTIES
    @property
    def upload_successful(self) -> bool:
        """
        Property providing a boolean indicating whether a file upload has been entirely successful.
        Note that n_model_instances_created is only set as the very last step of a successful upload.
        """
        return self.n_model_instances_created > 0
