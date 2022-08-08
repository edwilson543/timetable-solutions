
# Django imports
from django.shortcuts import render
from django.views.generic.edit import FormView


# Local application imports
from .forms import TeacherListUploadForm


class TeacherListUploadView(FormView):
    template_name = "file_upload_page.html"
    form_class = TeacherListUploadForm

    def post(self, request, *args, **kwargs):
        """Method for handling a POST request"""
        form = TeacherListUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pass
