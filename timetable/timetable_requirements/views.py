
# Standard library imports
from dataclasses import dataclass
from typing import Dict

# Django imports
from django.forms import Form
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.views.generic.base import View

# Local application imports
from .constants.csv_headers import CSVUplaodFiles
from data import models
from .forms import TeacherListUploadForm, PupilListUploadForm, ClassroomListUploadForm, TimetableStructureUploadForm, \
    UnsolvedClassUploadForm, FixedClassUploadForm
from .file_upload_processor import FileUploadProcessor


@dataclass
class RequiredUpload:
    """Dataclass to store information relating to each form"""
    form_name: str
    upload_status: str | bool
    empty_form: Form
    url_name: str

    def __post_init__(self):
        """Reset upload status to a string which is more easily rendered in the template, without unnecessary tags."""
        if self.upload_status:
            self.upload_status = "Complete"
        else:
            self.upload_status = "Incomplete"


# noinspection PyUnresolvedReferences
def _get_all_form_context(request: HttpRequest) -> Dict:
    """
    Function to get a dictionary of forms that must be populated (note each form has just one file field
    to allow files to be uploaded separately).
    """
    school_id = request.user.profile.school.school_access_key

    teacher_upload_status = len(models.Teacher.objects.filter(school_id=school_id)) > 0  # TODO move to models
    pupil_upload_status = len(models.Pupil.objects.filter(school_id=school_id)) > 0
    classroom_upload_status = models.Classroom.objects.school_has_classroom_data(school_id=school_id)
    timetable_upload_status = len(models.TimetableSlot.objects.filter(school_id=school_id)) > 0
    unsolved_class_upload_status = len(models.UnsolvedClass.objects.filter(school_id=school_id)) > 0
    fixed_class_upload_status = models.FixedClass.objects.school_has_user_defined_fixed_class_data(school_id=school_id)

    context = {"required_forms":
               {
                   "teachers": RequiredUpload(form_name="Teacher list", upload_status=teacher_upload_status,
                                              empty_form=TeacherListUploadForm(), url_name="teacher_list"),
                   "pupils": RequiredUpload(form_name="Pupil List", upload_status=pupil_upload_status,
                                            empty_form=PupilListUploadForm(), url_name="pupil_list"),
                   "classrooms": RequiredUpload(form_name="Classroom List", upload_status=classroom_upload_status,
                                                empty_form=ClassroomListUploadForm(), url_name="classroom_list"),
                   "timetable": RequiredUpload(form_name="Timetable Structure", upload_status=timetable_upload_status,
                                               empty_form=TimetableStructureUploadForm(),
                                               url_name="timetable_structure"),
                   "unsolved_classes": RequiredUpload(
                       form_name="Class requirements", upload_status=unsolved_class_upload_status,
                       empty_form=UnsolvedClassUploadForm(), url_name="unsolved_classes"),
                   "fixed_classes": RequiredUpload(
                       form_name="Fixed classes", upload_status=fixed_class_upload_status,
                       empty_form=FixedClassUploadForm(), url_name="fixed_classes")
               }
               }
    return context


def upload_page_view(request, error_message: str | None = None):
    """View called by the individual views for each of the form upload views."""
    template = loader.get_template("file_upload.html")
    context = _get_all_form_context(request=request)
    context["error_message"] = error_message
    return HttpResponse(template.render(context, request))


class TeacherListUploadView(View):
    """View to control upload of teacher list to database"""
    csv_headers = CSVUplaodFiles.TEACHERS.headers
    id_column_name = CSVUplaodFiles.TEACHERS.id_column
    model = models.Teacher

    # TODO add get request method

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = TeacherListUploadForm(request.POST, request.FILES)
        error_message = None
        if form.is_valid():
            file = request.FILES["teacher_list"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
            error_message = upload_processor.upload_error_message  # Will just be None if no errors

        return upload_page_view(request, error_message)


class PupilListUploadView(View):
    """View to control upload of pupil list to database"""
    csv_headers = CSVUplaodFiles.PUPILS.headers
    id_column_name = CSVUplaodFiles.PUPILS.id_column
    model = models.Pupil

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = PupilListUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["pupil_list"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)


class ClassroomListUploadView(View):
    """View to control upload of the classroom list to database"""
    csv_headers = CSVUplaodFiles.CLASSROOMS.headers
    id_column_name = CSVUplaodFiles.CLASSROOMS.id_column
    model = models.Classroom

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = ClassroomListUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["classroom_list"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)


class TimetableStructureUploadView(View):
    """View to control upload of the timetable structure to database"""
    csv_headers = CSVUplaodFiles.TIMETABLE.headers
    id_column_name = CSVUplaodFiles.TIMETABLE.id_column
    model = models.TimetableSlot

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = TimetableStructureUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["timetable_structure"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)


class UnsolvedClassUploadView(View):
    """View to control upload of the unsolved classes to the database"""
    csv_headers = CSVUplaodFiles.CLASS_REQUIREMENTS.headers
    id_column_name = CSVUplaodFiles.CLASS_REQUIREMENTS.id_column
    model = models.UnsolvedClass

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = UnsolvedClassUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["unsolved_classes"]
            upload_processor = FileUploadProcessor(
                is_unsolved_class_upload=True, csv_file=file, csv_headers=self.csv_headers,
                id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)


class FixedClassUploadView(View):
    """
    View to control upload of the fixed classes to the database (i.e. classes which are already known to have to
    occur at a certain times.
    """
    csv_headers = CSVUplaodFiles.FIXED_CLASSES.headers
    id_column_name = CSVUplaodFiles.FIXED_CLASSES.id_column
    model = models.FixedClass

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = FixedClassUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["fixed_classes"]
            upload_processor = FileUploadProcessor(
                is_fixed_class_upload=True, csv_file=file, csv_headers=self.csv_headers,
                id_column_name=self.id_column_name, model=self.model,
                school_access_key=request.user.profile.school.school_access_key)
        return upload_page_view(request)
