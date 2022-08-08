"""Module containing utility functions that are used to do the processing of the uploaded teacher files."""

# Standard library imports
from abc import ABC, abstractmethod
from csv import reader
from io import StringIO
from typing import List

# Django imports
from django.core.files.uploadedfile import UploadedFile

# Local application imports
from timetable.timetable_selector.models import Teacher


class FileUploadProcessor(ABC):
    """
    Abstract base class for the processing units which, following a POST request from the user involving a file
    upload, will take that file, check it fits the requirements, and then upload to the database or not as appropriate.
    """
    upload_status = False  # This only gets switched to True if a successful upload is made.

    def __init__(self, file: UploadedFile):
        self._upload_file_content(file=file)

    def _upload_file_content(self, file: UploadedFile) -> None:
        """Method to attempt to save the file to the database. If successful, upload status will become True."""
        file_bytes = file.readlines().decode("utf-8")
        file_stream = StringIO(file_bytes)
        csv_data = reader(file_stream, delimiter=",")

        for n, row in enumerate(csv_data):
            if n == 0:
                headers_valid = self._check_file_headers(header_row=row)
                if not headers_valid:
                    break
            else:
                row_valid = self._check_file_row(row=row)
                if not row_valid:
                    break
                self._upload_row_to_database(row=row)  # TODO can also implement this method within this class
        self.upload_status = True  # If the for loop gets completed, then the upload has succeeded

    @abstractmethod
    def _upload_row_to_database(self, row: List) -> None:
        """
        Method to save an individual row from the csv file to the database, once it has been validated.
        Note that one row from the csv file will correspond to one instance of the model.
        """
        # TODO this could just be created using an unpacking and an instance attribute
        raise NotImplementedError("Call made to abstract method _upload_ of ABC UploadFileProcessor")

    @abstractmethod
    def _check_file_headers(self, header_row: List) -> bool:
        """Method to check the correct file headers have been used. Returns True if they have been."""
        raise NotImplementedError("Call made to abstract method _check_file_headers of ABC UploadFileProcessor")

    @abstractmethod
    def _check_file_row(self, row: List) -> bool:
        """Method to validate the entries in file row. Returns True if the row is valid."""
        raise NotImplementedError("Call made to abstract method _check_file_row of ABC UploadFileProcessor")


class TeacherListUploadProcessor(FileUploadProcessor):
    """Class for handling the upload of teacher csv files from the user"""

    def __init__(self, file: UploadedFile):
        super().__init__(file)

    def _upload_file_content(self, file: UploadedFile) -> None:
        """Function to take the uploaded file object and save the data in the database."""





