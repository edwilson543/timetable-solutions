"""
Subclasses of the BaseFileUploadProcessor used to handle the upload of individual files.
"""

# Local application imports
from domain.data_upload_processing.base_file_upload_processor import (
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


class PupilFileUploadProcessor(BaseFileUploadProcessor):
    """
    Processor of csv files containing pupil data.
    """

    model = models.Pupil
    file_structure = UploadFileStructure.PUPILS


class TimetableFileUploadProcessor(BaseFileUploadProcessor):
    """
    Processor of csv files containing teacher data
    """

    model = models.TimetableSlot
    file_structure = UploadFileStructure.TIMETABLE
