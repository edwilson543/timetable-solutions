"""
Module containing utility class used to do the processing of the uploaded csv files into the database.
"""

# Standard library imports
import re
from io import StringIO

# Third party imports
import pandas as pd
from dateutil import parser as dateutil_parser  # type: ignore

# Django imports
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import IntegrityError, transaction

# Local application imports
from data import models
from domain.data_management.constants import FileStructure, Header


class BaseFileUploadProcessor:
    """
    Class for the processing unit which, following a POST request from the user involving a file upload, will take that
    file, check it fits the requirements, and then upload to the database or not as appropriate.
    This processor conducts the upload for the following models:
        - Teacher, Classroom, YearGroup, Pupil, TimetableSlot
    The class is subclassed to define the processing of uploaded 'Lesson' files.
    """

    # Class attributes set on each subclass
    model: type[models.ModelSubclass]  # Database table we are processing to
    file_structure: FileStructure  # Column headers and unique id_column in the file being processed

    __nan_handler = "###ignorenan"  # Used to fill na values in uploaded file, since float (nan) is error-prone

    def __init__(
        self,
        school_access_key: int,
        csv_file: UploadedFile,
        attempt_upload: bool = True,
    ):
        """
        :param school_access_key: Primary key of the school whose data is being processed
        :param csv_file: The file as received from the user upload
        :param attempt_upload: Whether to try to process the file's contents into the database.
        """
        # Instance attributes used internally
        self._school_access_key = school_access_key

        # Instance attributes that get set during upload, providing info on the level of success
        self.n_model_instances_created = 0
        self.upload_error_message: str | None = (
            None  # Provides details on why the upload has failed
        )

        # Try uploading the file to the database
        if attempt_upload:
            self._upload_file_content(file=csv_file)

    def _upload_file_content(self, file: UploadedFile) -> None:
        """
        Method to attempt to save the file to the database.
        Note that we either want all rows to become model instances or none of them to, hence we use an atomic
        transaction once we have cleaned all the data.
        """
        # Check the file type and then try to read it in as a csv
        file_extension = file.name.split(".")[1]
        if file_extension != "csv":
            self.upload_error_message = (
                f"Please upload your file as with the .csv!\n"
                f"File extension given was .{file_extension}."
            )
            return

        try:
            file_bytes = file.read().decode("utf-8")
            file_stream = StringIO(file_bytes)

            # noinspection PyTypeChecker
            upload_df = pd.read_csv(file_stream, sep=",")
        except UnicodeDecodeError:
            self.upload_error_message = (
                "Please check that your file is encoded using UTF-8!"
            )
            return
        except pd.errors.ParserError:
            self.upload_error_message = (
                "Bad file structure identified!\n"
                "Please check that data is only given under the defined columns."
            )
            return

        # Basic cleaning / checks on file content & structure
        upload_df.fillna(value=self.__nan_handler, inplace=True)
        upload_df.replace(to_replace="", value=self.__nan_handler)
        upload_df = self.convert_df_to_correct_types(upload_df)

        if not self._check_upload_df_structure_and_content(upload_df=upload_df):
            # Note that the error message attribute will be set as appropriate
            return

        # Process each file row into a dictionary to pass to create_new
        create_new_dict_list = self._get_data_dict_list_for_create_new(
            upload_df=upload_df
        )
        if create_new_dict_list is not None:
            try:
                with transaction.atomic():
                    for n, create_new_dict in enumerate(create_new_dict_list):
                        self.model.create_new(**create_new_dict)

                # Reaching this point means the upload processing has been successful
                self.n_model_instances_created = len(create_new_dict_list)

            except (
                ValidationError,  # Model does not pass the full_clean checks
                TypeError,  # Model was missing a required field (via the create_new method)
                ValueError,  # A string was passed to int(id_field)
            ) as debug_only_message:
                error = (
                    f"Could not interpret values in row {n+1} as a {self.model.Constant.human_string_singular}!"
                    f"\nPlease check that all data is of the correct type and all ids referenced are in use!"
                )
                self.upload_error_message = error
                if settings.DEBUG:
                    self.upload_error_message = str(debug_only_message)
            except IntegrityError as debug_only_message:
                error = f"ID given for {self.model.Constant.human_string_singular} in row {n + 1} was not unique!"
                self.upload_error_message = error
                if settings.DEBUG:
                    self.upload_error_message = str(debug_only_message)
            except ObjectDoesNotExist as debug_only_message:
                self.upload_error_message = (
                    f"Row {n + 1} of your file referenced a year group / pupil / teacher / classroom / "
                    f"timetable slot id which does not exist!\n Please check this!"
                )
                if settings.DEBUG:
                    self.upload_error_message = str(debug_only_message)

            except Exception:
                # Just in case, catch any other exception that may occur
                self.upload_error_message = (
                    f"Could not process {self.model.Constant.human_string_singular} "
                    f"in row {n + 1} of your file. Please amend!"
                )

    def _get_data_dict_list_for_create_new(
        self, upload_df: pd.DataFrame
    ) -> list[dict] | None:
        """
        Method to iterate through the rows of the dataframe, and create a list of dictionaries that can be passed to
        self._model.create_new(**create_new_dict).
        """
        create_new_dict_list: list[dict] = []
        row_number = 1  # row_number is only used for user-targeted error messages, so count from 1 not 0

        for _, data_ser in upload_df.iterrows():
            create_new_dict = self._get_data_dict_from_row_for_create_new(
                row=data_ser, row_number=row_number
            )

            # dict-getting methods will set errors, so if there is / isn't one set, proceed as appropriate
            if create_new_dict and not self.upload_error_message:
                create_new_dict_list.append(create_new_dict)
                row_number += 1
            else:
                # A single error means we write off the entire file contents
                return None

        return create_new_dict_list

    def _get_data_dict_from_row_for_create_new(
        self, row: pd.Series, row_number: int
    ) -> dict:
        """
        Method to take an individual row from the csv file, and convert it into a dictionary which can be passed
        directly to self._model.create_new(**create_new_dict) to initialise a model instance
        :return dictionary mapping create_new kwargs to the field values of self._model
        """
        initial_create_new_dict = row.to_dict()
        create_new_dict = {
            key: value
            for key, value in initial_create_new_dict.items()
            if value != self.__nan_handler
        }
        create_new_dict[Header.SCHOOL_ID] = self._school_access_key

        return create_new_dict

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
        if len(upload_df.columns) == len(self.file_structure.headers):
            headers_valid = all(upload_df.columns == self.file_structure.headers)
            if not headers_valid:
                self.upload_error_message = headers_error
                return False
        else:
            self.upload_error_message = headers_error
            return False

        # Check that the id column contains no duplicates
        if self.file_structure.id_column is not None:
            # This needs to be done upfront, as .validate_unique() called by .full_clean() is redundant here
            ids_unique = upload_df[self.file_structure.id_column].is_unique
            if not ids_unique:
                self.upload_error_message = (
                    "Input file contained repeated ids "
                    f"(id column is {self.file_structure.id_column})"
                )
                return False

        # All checks have passed so return True
        return True

    # COLUMN-BY-COLUMN PROCESSING
    def convert_df_to_correct_types(self, upload_df: pd.DataFrame) -> pd.DataFrame:
        """
        Hook to allow subclasses to implement custom logic for individual columns.
        Shared implementation provided.
        """
        try:
            if Header.STARTS_AT in upload_df.columns:
                upload_df[Header.STARTS_AT] = pd.to_datetime(
                    upload_df[Header.STARTS_AT]
                )
            if Header.ENDS_AT in upload_df.columns:
                upload_df[Header.ENDS_AT] = pd.to_datetime(upload_df[Header.ENDS_AT])
        except dateutil_parser.ParserError:
            self.upload_error_message = (
                "Could not interpret given start / end times as valid times. "
                "Please supply them in the format: 'HH:MM' e.g. 08:00; 15:00"
            )
        return upload_df

    # PROPERTIES
    @property
    def upload_successful(self) -> bool:
        """
        Property providing a boolean indicating whether a file upload has been entirely successful.
        Note that n_model_instances_created is only set as the very last step of a successful upload.
        """
        return self.n_model_instances_created > 0


class RelationalUploadProcessorMixin:
    """
    Mixin allowing processing of columns representing foreign key and many-to-many relationships.

    For example, extracting the pupil ids the user is trying to reference via the string '1; 2; 3' in a column
    called 'pupil_ids', or the teacher id from a 'teacher_id' column
    """

    _school_access_key: int
    upload_error_message: str | None = None

    allowed_id_join_characters = r"[:;&-]"  # i.e. multi-id column could be: 1;2 etc.

    # --------------------
    # Processing of columns shared across files
    # --------------------

    def _get_year_groups_from_raw_year_group_string(
        self,
        raw_year_group_string: str,
        row_number: int,
    ) -> models.YearGroupQuerySet | None:
        """
        Method providing a reduced entry point to M2MUploadProcessorMixin's get_id_set_from_string method,
        by only offering 2 of the arguments (which is what we always want for this processor.

        :return A set of ids, representing pupil ids or timetable slot ids.
        """

        year_group_ids = self.get_integer_set_from_string(
            raw_string_of_ids=raw_year_group_string,
            row_number=row_number,
        )
        if year_group_ids is None or len(year_group_ids) == 0:
            self.upload_error_message = (
                f"Invalid year groups: {raw_year_group_string} in row: {row_number}. "
                f"Please amend!"
            )
            return None

        year_groups = models.YearGroup.objects.get_specific_year_groups(
            school_id=self._school_access_key, year_group_ids=year_group_ids
        )

        if year_groups.count() < len(year_group_ids):
            missing_year_groups = year_group_ids - {yg.year_group for yg in year_groups}
            self.upload_error_message = (
                f"No year_group(s) with ids: {missing_year_groups} were found, "
                f"referenced in row {row_number}!"
            )
            return None

        return year_groups

    # --------------------
    # Generic logic for processing related columns
    # --------------------

    def get_integer_set_from_string(
        self,
        raw_string_of_ids: str,
        row_number: int,
    ) -> frozenset[int] | None:
        """
        Method to get a set of integer ids from a raw string take from the user's uploaded file

        :param raw_string_of_ids: The raw content of a cell in the user's csv file.
        :param row_number: The row the raw string originated from (for error messages).

        :return A set of ids, representing e.g. some pupil or teacher ids.

        :side effects: To set the upload_error_message instance attribute, if an error is encountered.
        """
        # Clean up the string and make it into a list
        raw_string_of_ids = re.sub(
            self.allowed_id_join_characters, ",", str(raw_string_of_ids)
        )

        # Prune out any invalid characters
        valid_id_chars = ",0123456789"
        raw_string_of_ids = "".join(
            [
                character
                for character in raw_string_of_ids
                if character in valid_id_chars
            ]
        )

        # Remove double commas
        raw_string_of_ids = re.sub(r",+", ",", raw_string_of_ids)
        if len(raw_string_of_ids) == 0 or raw_string_of_ids == ",":
            # This isn't an issue directly, so just return None here
            return None

        # Make string into python list syntax
        if raw_string_of_ids[0] == ",":
            raw_string_of_ids = raw_string_of_ids[1:]

        # Try to convert the string as a python list
        try:
            id_list = self._process_string_to_list(
                comma_separated_string=raw_string_of_ids,
            )
            unique_id_set = frozenset(value for value in id_list)
            return unique_id_set

        except ValueError:
            error = f"Could not interpret contents of: {row_number} as integers! Please use the format: '1; 2; 3;'"
            self.upload_error_message = error

        return None

    def get_clean_id_from_file_field_value(
        self, user_input_id: str | int | float | None, row_number: int, field_name: str
    ) -> int | None:
        """
        Method to clean a string the user has entered which should just be a single number (or None).
        We use get_integer_set_from_string, and then return the single integer or None, in the case where the user
        has not given a valid value (which may not be an issue, since some id fields are nullable).
        """
        if user_input_id is not None:
            user_input_id = str(user_input_id)
            user_input_id_no_floats = re.sub(
                r"[.].+", "", user_input_id  # User's id may be read-in as '10.0'
            )
            id_set = self.get_integer_set_from_string(
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

    @staticmethod
    def _process_string_to_list(comma_separated_string: str) -> list[int]:
        """
        Method to create a list from a comma separated string.

        :param comma_separated_string: A string originating from a single entry of the user's uploaded file

        e.g. take: '1,2,3,4' and return ['1', '2', '3', '4']
        """
        lis = []
        current_component = ""
        for character in comma_separated_string:
            if character == ",":
                lis.append(int(current_component.replace(" ", "")))
                current_component = ""
            else:
                current_component += character

        # Ensure the final current component gets added to the list
        if current_component not in lis and current_component != "":
            lis.append(int(current_component.replace(" ", "")))

        return lis
