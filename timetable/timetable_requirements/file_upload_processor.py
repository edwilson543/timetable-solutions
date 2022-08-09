"""Module containing utility class used to do the processing of the uploaded csv files into the database."""

# Standard library imports
from io import StringIO
from typing import List, Type, TypeVar

# Third party imports
import pandas as pd
from pandas import read_csv

# Django imports
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Model


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
                 model: Type[ModelInstance]):
        """
        :param csv_file: the file as received from the user upload
        :param csv_headers: the column headers from the csv file, which will correspond to the model fields
        :param id_column_name: whether or not the input file should contain an id column
        :param model: the model that the file is used to create instances of
        """
        self._csv_headers = csv_headers
        self._id_column_name = id_column_name
        self._model = model

        # Try uploading the file to the database
        self.upload_successful = False  # This only gets switched to True if a successful upload is made.
        self._upload_file_content(file=csv_file)

    def _upload_file_content(self, file: UploadedFile) -> None:
        """Method to attempt to save the file to the database. If successful, upload status will become True."""
        file_bytes = file.read().decode("utf-8")
        file_stream = StringIO(file_bytes)
        # noinspection PyTypeChecker
        upload_df = read_csv(file_stream, sep=",")

        # Check file structure and id column uniqueness where relevant
        headers_valid = upload_df.columns == self._csv_headers
        if not headers_valid:
            return
        if self._id_column_name is not None:
            # This needs to be done upfront, as .validate_unique() called by .full_clean() is redundant below
            ids_unique = upload_df[self._id_column_name].is_unique
            if not ids_unique:
                return

        # Check rows for valid model instances and accumulate (until an error is found)
        valid_model_instances = []
        for _, data_ser in upload_df.iterrows():
            model_instance = self._create_model_instance_from_row(row=data_ser)
            if model_instance is None:
                break
            valid_model_instances.append(model_instance)  # Cant yet upload to database, if later row invalid

        # Full file now check, so upload all model instances to the database
        for model in valid_model_instances:
            model.save()
        self.upload_successful = True

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
