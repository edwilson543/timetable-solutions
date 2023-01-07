"""
Views relating to the upload of user data - each subclass of DataUploadBase handles the upload of one specific csv file.
"""

# Local application imports
from domain import data_upload_processing
from interfaces.data_upload import forms
from .base_classes import DataUploadBase


class TeacherListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of teachers by the user
    """

    form = forms.TeacherListUpload
    processor = data_upload_processing.TeacherFileUploadProcessor


class ClassroomListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of classrooms by the user
    """

    form = forms.ClassroomListUpload
    processor = data_upload_processing.ClassroomFileUploadProcessor


class YearGroupListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of year groups by the user
    """

    form = forms.YearGroupUpload
    processor = data_upload_processing.YearGroupFileUploadProcessor


class PupilListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of pupils by the user
    """

    form = forms.PupilListUpload
    processor = data_upload_processing.PupilFileUploadProcessor


class TimetableStructureUpload(DataUploadBase):
    """
    View class to control the uploading of the list of teachers by the user
    """

    form = forms.TimetableStructureUpload
    processor = data_upload_processing.TimetableSlotFileUploadProcessor


class LessonsUpload(DataUploadBase):
    """
    View class to control the uploading of the requirements for classes that must take place by the user
    """

    form = forms.LessonUpload
    processor = data_upload_processing.LessonFileUploadProcessor
