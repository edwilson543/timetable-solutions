"""
Views relating to the upload of user data - each subclass of DataUploadView handles the upload of one specific csv file.
"""

# Local application imports
from data import models
from domain import data_upload_processing
from interfaces.data_upload import forms
from .upload_view_base_class import DataUploadView


class TeacherListUpload(DataUploadView):
    """View class to control the uploading of the list of teachers by the user"""
    def __init__(self):
        super().__init__(
            file_structure=data_upload_processing.constants.UploadFileStructure.TEACHERS,
            model=models.Teacher,
            target_model_name="teachers",
            form=forms.TeacherListUpload
        )


class PupilListUpload(DataUploadView):
    """View class to control the uploading of the list of pupils by the user"""
    def __init__(self):
        super().__init__(
            file_structure=data_upload_processing.constants.UploadFileStructure.PUPILS,
            model=models.Pupil,
            target_model_name="pupils",
            form=forms.PupilListUpload
        )


class ClassroomListUpload(DataUploadView):
    """View class to control the uploading of the list of classrooms by the user"""
    def __init__(self):
        super().__init__(
            file_structure=data_upload_processing.constants.UploadFileStructure.CLASSROOMS,
            model=models.Classroom,
            target_model_name="classrooms",
            form=forms.ClassroomListUpload
        )


class TimetableStructureUpload(DataUploadView):
    """View class to control the uploading of the list of teachers by the user"""
    def __init__(self):
        super().__init__(
            file_structure=data_upload_processing.constants.UploadFileStructure.TIMETABLE,
            model=models.TimetableSlot,
            target_model_name="timetable slots",
            form=forms.TimetableStructureUpload
        )


class UnsolvedClassUpload(DataUploadView):
    """View class to control the uploading of the requirements for classes that must take place by the user"""
    def __init__(self):
        super().__init__(
            file_structure=data_upload_processing.constants.UploadFileStructure.UNSOLVED_CLASSES,
            model=models.UnsolvedClass,
            form=forms.UnsolvedClassUpload,
            target_model_name="required classes",
            is_unsolved_class_upload_view=True
        )


class FixedClassUpload(DataUploadView):
    """View class to control the uploading of the list of classes that must occur at a certain time by the user"""
    def __init__(self):
        super().__init__(
            file_structure=data_upload_processing.constants.UploadFileStructure.FIXED_CLASSES,
            model=models.FixedClass,
            target_model_name="fixed classes",
            form=forms.FixedClassUpload,
            is_fixed_class_upload_view=True
        )
