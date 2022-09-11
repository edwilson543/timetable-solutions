
# Django imports
from django.views.generic.base import View

# Local application imports
from data import models
from domain import data_upload_processing
from interfaces.data_upload import forms
from .forms import TeacherListUpload, PupilListUpload, ClassroomListUpload, TimetableStructureUpload, \
    UnsolvedClassUpload, FixedClassUpload
from .upload_view_base_class import upload_page_view
from .upload_view_base_class import DataUploadView


class TeacherListUploadView(DataUploadView):
    """View class to control the uploading of the list of teachers by the user"""
    def __init__(self):
        super().__init__(
            file_structure=data_upload_processing.constants.UploadFileStructure.TEACHERS,
            model=models.Teacher,
            form=forms.TeacherListUpload)


class PupilListUploadView(View):
    """View to control upload of pupil list to database"""
    csv_headers = data_upload_processing.UploadFileStructure.PUPILS.headers
    id_column_name = data_upload_processing.UploadFileStructure.PUPILS.id_column
    model = models.Pupil

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = PupilListUpload(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["pupil_list"]
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)


class ClassroomListUploadView(View):
    """View to control upload of the classroom list to database"""
    csv_headers = data_upload_processing.UploadFileStructure.CLASSROOMS.headers
    id_column_name = data_upload_processing.UploadFileStructure.CLASSROOMS.id_column
    model = models.Classroom

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = ClassroomListUpload(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["classroom_list"]
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)


class TimetableStructureUploadView(View):
    """View to control upload of the timetable structure to database"""
    csv_headers = data_upload_processing.UploadFileStructure.TIMETABLE.headers
    id_column_name = data_upload_processing.UploadFileStructure.TIMETABLE.id_column
    model = models.TimetableSlot

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = TimetableStructureUpload(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["timetable_structure"]
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)


class UnsolvedClassUploadView(View):
    """View to control upload of the unsolved classes to the database"""
    csv_headers = data_upload_processing.UploadFileStructure.CLASS_REQUIREMENTS.headers
    id_column_name = data_upload_processing.UploadFileStructure.CLASS_REQUIREMENTS.id_column
    model = models.UnsolvedClass

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = UnsolvedClassUpload(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["unsolved_classes"]
            upload_processor = data_upload_processing.FileUploadProcessor(
                is_unsolved_class_upload=True, csv_file=file, csv_headers=self.csv_headers,
                id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)


class FixedClassUploadView(View):
    """
    View to control upload of the fixed classes to the database (i.e. classes which are already known to have to
    occur at a certain times.
    """
    csv_headers = data_upload_processing.UploadFileStructure.FIXED_CLASSES.headers
    id_column_name = data_upload_processing.UploadFileStructure.FIXED_CLASSES.id_column
    model = models.FixedClass

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = FixedClassUpload(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["fixed_classes"]
            upload_processor = data_upload_processing.FileUploadProcessor(
                is_fixed_class_upload=True, csv_file=file, csv_headers=self.csv_headers,
                id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)
