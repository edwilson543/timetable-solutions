"""
Subclasses of the BaseFileUploadProcessor used to handle the upload of individual files
that contain no relational data.
"""


# Local application imports
from data import models
from domain.data_management.classrooms import operations as classroom_operations
from domain.data_management.constants import UploadFileStructure
from domain.data_management.teachers import operations as teacher_operations
from domain.data_management.upload_processors._base import BaseFileUploadProcessor
from domain.data_management.year_groups import operations as year_group_operations


class TeacherFileUploadProcessor(BaseFileUploadProcessor):
    """
    Processor of csv files containing teacher data.
    """

    model = models.Teacher
    file_structure = UploadFileStructure.TEACHERS
    creation_callback = teacher_operations.create_new_teacher


class ClassroomFileUploadProcessor(BaseFileUploadProcessor):
    """
    Processor of csv files containing classroom data.
    """

    model = models.Classroom
    file_structure = UploadFileStructure.CLASSROOMS
    creation_callback = classroom_operations.create_new_classroom


class YearGroupFileUploadProcessor(BaseFileUploadProcessor):
    """
    Processor of csv files containing year group data.
    """

    model = models.YearGroup
    file_structure = UploadFileStructure.YEAR_GROUPS
    creation_callback = year_group_operations.create_new_year_group
