"""
Views relating to the upload of user data - each subclass of DataUploadBase handles the upload of one specific csv file.
"""

# Local application imports
from domain import data_management
from interfaces.data_management import forms_legacy
from .base_classes import DataUploadBase


class TeacherListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of teachers by the user
    """

    form = forms_legacy.TeacherListUpload
    processor = data_management.TeacherFileUploadProcessor


class ClassroomListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of classrooms by the user
    """

    form = forms_legacy.ClassroomListUpload
    processor = data_management.ClassroomFileUploadProcessor


class YearGroupListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of year groups by the user
    """

    form = forms_legacy.YearGroupUpload
    processor = data_management.YearGroupFileUploadProcessor


class PupilListUpload(DataUploadBase):
    """
    View class to control the uploading of the list of pupils by the user
    """

    form = forms_legacy.PupilListUpload
    processor = data_management.PupilFileUploadProcessor


class TimetableStructureUpload(DataUploadBase):
    """
    View class to control the uploading of the list of teachers by the user
    """

    form = forms_legacy.TimetableStructureUpload
    processor = data_management.TimetableSlotFileUploadProcessor


class LessonsUpload(DataUploadBase):
    """
    View class to control the uploading of lesson instances
    """

    form = forms_legacy.LessonUpload
    processor = data_management.LessonFileUploadProcessor


class BreaksUpload(DataUploadBase):
    """
    View class to control the uploading of break instances
    """

    form = forms_legacy.BreakUpload
    processor = data_management.BreakFileUploadProcessor
