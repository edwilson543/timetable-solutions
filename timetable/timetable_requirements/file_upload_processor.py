"""Module containing utility class used to do the processing of the uploaded csv files into the database."""

# Standard library imports
import ast
from io import StringIO
from typing import List, Type, TypeVar

# Third party imports
import pandas as pd
from pandas import read_csv

# Django imports
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Model

# Local application imports
from timetable_selector.models import Pupil
from .models import UnsolvedClass

ModelInstance = TypeVar("ModelInstance", bound=Model)  # Typehint when referring to specific django Model subclasses


class FileUploadProcessor:
    """
    Class for the processing unit which, following a POST request from the user involving a file upload, will take that
    file, check it fits the requirements, and then upload to the database or not as appropriate.
    """

    def __init__(self,
                 csv_file: UploadedFile,
                 csv_headers: List[str],
                 id_column_name: str | None,
                 model: Type[ModelInstance],
                 is_unsolved_class_upload: bool = False,
                 is_fixed_class_upload: bool = False):
        """
        :param csv_file: the file as received from the user upload
        :param csv_headers: the column headers from the csv file, which will correspond to the model fields
        :param id_column_name: string depending on whether the input file contains an id column
        :param model: the model that the file is used to create instances of

        :param is_unsolved_class_upload/is_fixed_class_upload - these represent special cases of the file upload
        process since the models the data are being uploaded to contain many-to-many relationships, and thus require
        their own methods (see _create_model_instance_from_row variations below)
        """
        self._csv_headers = csv_headers
        self._id_column_name = id_column_name
        self._model = model
        self._is_unsolved_class_upload = is_unsolved_class_upload
        self._is_fixed_class_upload = is_fixed_class_upload

        # Try uploading the file to the database
        self.upload_successful = False  # This only gets switched to True if a successful upload is made.
        self._upload_file_content(file=csv_file)

    def _upload_file_content(self, file: UploadedFile) -> None:
        """Method to attempt to save the file to the database. If successful, upload status will become True."""
        file_bytes = file.read().decode("utf-8")
        file_stream = StringIO(file_bytes)
        # noinspection PyTypeChecker
        upload_df = read_csv(file_stream, sep=",")

        if not self._check_headers_valid_and_ids_unique(upload_df=upload_df):
            return

        valid_model_instances = self._get_valid_model_instances(upload_df=upload_df)

        if valid_model_instances is None:
            return
        for model in valid_model_instances:
            model.save()
        self.upload_successful = True

    def _check_headers_valid_and_ids_unique(self, upload_df: pd.DataFrame) -> bool:
        headers_valid = all(upload_df.columns == self._csv_headers)
        if not headers_valid:
            return False
        if self._id_column_name is not None:
            # This needs to be done upfront, as .validate_unique() called by .full_clean() is redundant below
            ids_unique = upload_df[self._id_column_name].is_unique
            if not ids_unique:
                return False
        return True

    def _get_valid_model_instances(self, upload_df: pd.DataFrame) -> List | None:
        valid_model_instances = []
        for _, data_ser in upload_df.iterrows():
            if self._is_unsolved_class_upload:
                model_instance = self._create_unsolved_class_instance_from_row(row=data_ser)
                if model_instance is None:
                    return None
                valid_model_instances.append(model_instance)  # Cant yet upload to database, if later row invalid
            else:
                model_instance = self._create_model_instance_from_row(row=data_ser)
                if model_instance is None:
                    return None
                valid_model_instances.append(model_instance)

        return valid_model_instances

    def _create_model_instance_from_row(self, row: pd.Series) -> Type[ModelInstance] | None:
        """
        Method to take an individual row from the csv file, validate that it corresponds to a valid model instance,
        and then create that model instance.
        """
        model_dict = row.to_dict()
        try:
            model_instance = self._model(**model_dict)
            model_instance.full_clean()
            return model_instance
        except ValidationError:
            return None

    @staticmethod
    def _create_unsolved_class_instance_from_row(row: pd.Series) -> UnsolvedClass | None:
        """Method to process each row of the unsolved class csv file upload"""
        model_dict = {"class_id": row["class_id"], "subject_name": row["subject_name"], "teacher_id": row["teacher_id"],
                      "classroom_id": row["classroom_id"], "total_slots": row["total_slots"],
                      "min_slots": row["min_slots"]}  # Note we don't include the pupil_ids here
        try:
            model_instance = UnsolvedClass(**model_dict)
            pups = ast.literal_eval(row["pupil_ids"])
            pups = {int(val) for val in pups}
            model_instance.pupils.add(*pups)
            model_instance.full_clean()
            return model_instance
        except ValidationError:
            return None
