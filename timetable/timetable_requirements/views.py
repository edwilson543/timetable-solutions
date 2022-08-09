
# Django imports
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.generic.base import View

# Local application imports
from .forms import TeacherListUploadForm
from .file_upload_processor import FileUploadProcessor
from timetable_selector.models import Teacher


def get_all_forms():
    """This will be updated to be from an upload status model."""
    return {"teacher_form": TeacherListUploadForm()}


def upload_page_view(request):
    """Initial view for loading the upload page."""
    template = loader.get_template("file_upload.html")
    context = get_all_forms()
    return HttpResponse(template.render(context, request))


class TeacherListUploadView(View):
    template_name = "file_upload.html"
    csv_headers = ["teacher_id", "firstname", "surname", "title"]
    id_column_name = "teacher_id"
    model = Teacher

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = TeacherListUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            upload_processor = FileUploadProcessor(
                csv_file=file, csv_headers=self.csv_headers, id_column_name=self.id_column_name, model=self.model)
            if upload_processor.upload_successful:
                context = {
                    "placeholder": True
                }
                return render(request, self.template_name, context)

