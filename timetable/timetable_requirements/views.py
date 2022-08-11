
# Standard library imports
from dataclasses import dataclass
from typing import Dict

# Django imports
from django.forms import Form
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.generic.base import View

# Local application imports
from .forms import TeacherListUploadForm
from .file_upload_processor import FileUploadProcessor
from timetable_selector.models import Teacher


@dataclass
class RequiredUpload:
    """Dataclass to store information relating to each form"""
    form_name: str
    upload_status: str | bool
    empty_form: Form

    def __post_init__(self):
        """Reset upload status to a string which is more easily rendered in the template, without unnecessary tags."""
        if self.upload_status:
            self.upload_status = "Complete"
        else:
            self.upload_status = "Incomplete"


def _get_all_form_context() -> Dict:
    """Function to get a dictionary of forms that must be populated (note each form has just one file field
    to allow files to be uploaded separately)."""
    teacher_upload_status = len(Teacher.objects.all()) > 0
    context = {"teachers": RequiredUpload(form_name="Teacher list", upload_status=teacher_upload_status,
                                          empty_form=TeacherListUploadForm())}
    return context


def upload_page_view(request):
    """Initial view for loading the upload page."""
    template = loader.get_template("file_upload.html")
    context = _get_all_form_context()
    return HttpResponse(template.render(context, request))


class TeacherListUploadView(View):
    """View to control upload of teacher list to database"""
    template_name = "file_upload.html"
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
        context = _get_all_form_context()
        return render(request, self.template_name, context)

