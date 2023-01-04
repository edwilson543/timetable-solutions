"""
Views relating to the upload of user data - each subclass of DataUploadBase handles the upload of one specific csv file.
"""

# Local application imports
from data import models
from domain import data_upload_processing
from interfaces.data_upload import forms
from .base_classes import DataUploadBase


class TeacherListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of teachers by the user
    """

    file_structure = data_upload_processing.constants.UploadFileStructure.TEACHERS
    model = models.Teacher
    form = forms.TeacherListUpload
    processor = data_upload_processing.FileUploadProcessor


class ClassroomListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of classrooms by the user
    """

    file_structure = data_upload_processing.constants.UploadFileStructure.CLASSROOMS
    model = models.Classroom
    form = forms.ClassroomListUpload
    processor = data_upload_processing.FileUploadProcessor


class YearGroupListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of year groups by the user
    """

    file_structure = data_upload_processing.constants.UploadFileStructure.YEAR_GROUPS
    model = models.YearGroup
    form = forms.YearGroupUpload
    processor = data_upload_processing.FileUploadProcessor


class PupilListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of pupils by the user
    """

    file_structure = data_upload_processing.constants.UploadFileStructure.PUPILS
    model = models.Pupil
    form = forms.PupilListUpload
    processor = data_upload_processing.FileUploadProcessor


class TimetableStructureUpload(DataUploadBase):
    """
    View class to control the uploading of the list of teachers by the user
    """

    file_structure = data_upload_processing.constants.UploadFileStructure.TIMETABLE
    model = models.TimetableSlot
    form = forms.TimetableStructureUpload
    processor = data_upload_processing.FileUploadProcessor


class LessonsUpload(DataUploadBase):
    """
    View class to control the uploading of the requirements for classes that must take place by the user
    """

    file_structure = data_upload_processing.constants.UploadFileStructure.LESSON
    model = models.Lesson
    form = forms.LessonUpload
    processor = data_upload_processing.LessonFileUploadProcessor
