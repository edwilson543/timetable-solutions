
# Standard library imports
from dataclasses import dataclass
from typing import Dict

# Django imports
from django.forms import Form
from django.http import HttpResponse
from django.template import loader
from django.views.generic.base import View

# Local application imports
from .forms import TeacherListUploadForm, PupilListUploadForm, ClassroomListUploadForm, TimetableStructureUploadForm, \
    UnsolvedClassUploadForm
from .file_upload_processor import FileUploadProcessor
from .models import UnsolvedClass
from timetable_selector.models import Teacher, Pupil, Classroom, TimetableSlot


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
def _get_all_form_context() -> Dict:
    """Function to get a dictionary of forms that must be populated (note each form has just one file field
    to allow files to be uploaded separately)."""
    teacher_upload_status = len(Teacher.objects.all()) > 0  # In due course, status will depend on authenticated user
    pupil_upload_status = len(Pupil.objects.all()) > 0
    classroom_upload_status = len(Classroom.objects.all()) > 0
    timetable_upload_status = len(TimetableSlot.objects.all()) > 0
    unsolved_class_upload_status = len(UnsolvedClass.objects.all()) > 0
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
                       empty_form=UnsolvedClassUploadForm(), url_name="unsolved_classes")
               }
               }
    return context


def upload_page_view(request):
    """Initial view for loading the upload page."""
    template = loader.get_template("file_upload.html")
    context = _get_all_form_context()
    return HttpResponse(template.render(context, request))


class TeacherListUploadView(View):
    """View to control upload of teacher list to database"""
    csv_headers = ["teacher_id", "firstname", "surname", "title"]
    id_column_name = "teacher_id"
    model = Teacher

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = TeacherListUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["teacher_list"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model)
        return upload_page_view(request)


class PupilListUploadView(View):
    """View to control upload of pupil list to database"""
    csv_headers = ["pupil_id", "firstname", "surname", "year_group"]
    id_column_name = "pupil_id"
    model = Pupil

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = PupilListUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["pupil_list"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model)
        return upload_page_view(request)


class ClassroomListUploadView(View):
    """View to control upload of the classroom list to database"""
    csv_headers = ["classroom_id", "building", "room_number"]
    id_column_name = "classroom_id"
    model = Classroom

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = ClassroomListUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["classroom_list"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model)
        return upload_page_view(request)


class TimetableStructureUploadView(View):
    """View to control upload of the timetable structure to database"""
    csv_headers = ["slot_id", "day_of_week", "period_start_time", "period_duration"]
    id_column_name = "slot_id"
    model = TimetableSlot

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = TimetableStructureUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["timetable_structure"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model)
        return upload_page_view(request)


class UnsolvedClassUploadView(View):
    """View to control upload of the unsolved classes to the database"""
    csv_headers = ["class_id", "subject_name", "teacher_id", "pupil_ids", "classroom_id", "total_slots", "min_slots"]
    id_column_name = "class_id"
    model = UnsolvedClass

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = UnsolvedClassUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["unsolved_classes"]
            upload_processor = FileUploadProcessor(is_unsolved_class_upload=True,
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model)
        return upload_page_view(request)
