"""
Subclasses of the BaseFileUploadProcessor used to handle the upload of individual files
that contain no relational data.
"""


# Local application imports
from domain.data_upload_processing.processors._base import (
    BaseFileUploadProcessor,
)
from domain.data_upload_processing.constants import UploadFileStructure
from data import models


class TeacherFileUploadProcessor(BaseFileUploadProcessor):
    """
    Processor of csv files containing teacher data.
    """

    model = models.Teacher
    file_structure = UploadFileStructure.TEACHERS


class ClassroomFileUploadProcessor(BaseFileUploadProcessor):
    """
    Processor of csv files containing classroom data.
    """

    model = models.Classroom
    file_structure = UploadFileStructure.CLASSROOMS


class YearGroupFileUploadProcessor(BaseFileUploadProcessor):
    """
    Processor of csv files containing year group data.
    """

    model = models.YearGroup
    file_structure = UploadFileStructure.YEAR_GROUPS
