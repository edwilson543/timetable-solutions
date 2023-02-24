"""
Subclasses of the BaseFileUploadProcessor used to handle the upload of individual files
that contain no relational data.
"""


# Local application imports
from data import models
from domain.data_management.constants import UploadFileStructure
from domain.data_management.upload_processors._base import BaseFileUploadProcessor


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
