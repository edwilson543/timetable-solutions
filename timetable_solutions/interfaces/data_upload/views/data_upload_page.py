"""
Module defining the data upload page, its context, and required ancillaries.
"""

# Standard library imports
from dataclasses import dataclass
from typing import Dict

# Django imports
from django import urls, forms, http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# Local application imports
from constants.url_names import UrlName, ExampleFile
from domain import data_upload_processing
from interfaces.data_upload import forms


@dataclass(frozen=True)
class RequiredUpload:
    """
    Dataclass to store information relating to an individual required upload (form).
    This is used to control how the corresponding row of the table containing file uploads is rendered - e.g. whether
    to mark a form as complete and offer a reset button, or as incomplete and to offer an upload button.
    It also stores the urls related to different actions.
    """
    form_name: str  # Name of the form that will be shown to the user
    upload_status: data_upload_processing.UploadStatus  # User interpretable status string
    empty_form: forms.Form
    upload_url_name: UrlName
    reset_url_name:  UrlName
    example_download_absolute_url: str  # provided by the ExampleFile Enum


class UploadPage(LoginRequiredMixin, TemplateView):
    """
    Template view with the following main purposes:
        - Handling HTTP to the base data upload page (whose url this class is attached to)
        - Defining the logic for gathering all the required upload forms into one set of context data
        - Being subclassed, to provide its rendering of the data upload page (with the full context) to other views.
    """

    login_url = urls.reverse_lazy("login")
    template_name = "file_upload.html"

    def get_context_data(self, *args, **kwargs) -> Dict[str, Dict[str, RequiredUpload]]:
        """
        Method to get a dictionary of 'RequiredUpload' instances which are used to then control the rendering of either
        an empty form, or a completion message.
        We retrieve the upload status of each of the necessary datasets for the given school
        """
        school = self.request.user.profile.school
        upload_status = data_upload_processing.UploadStatusTracker.get_upload_status(school=school)

        context = {
            "required_forms": {
                    "pupils": RequiredUpload(form_name="Pupils", upload_status=upload_status.pupils,
                                             empty_form=forms.PupilListUpload(),
                                             upload_url_name=UrlName.PUPIL_LIST_UPLOAD.value,
                                             reset_url_name=UrlName.PUPIL_LIST_RESET.value,
                                             example_download_absolute_url=ExampleFile.PUPILS.url),
                    "teachers": RequiredUpload(form_name="Teachers", upload_status=upload_status.teachers,
                                               empty_form=forms.TeacherListUpload(),
                                               upload_url_name=UrlName.TEACHER_LIST_UPLOAD.value,
                                               reset_url_name=UrlName.TEACHER_LIST_RESET.value,
                                               example_download_absolute_url=ExampleFile.TEACHERS.url),
                    "classrooms": RequiredUpload(form_name="Classrooms", upload_status=upload_status.classrooms,
                                                 empty_form=forms.ClassroomListUpload(),
                                                 upload_url_name=UrlName.CLASSROOM_LIST_UPLOAD.value,
                                                 reset_url_name=UrlName.CLASSROOM_LIST_RESET.value,
                                                 example_download_absolute_url=ExampleFile.CLASSROOMS.url),
                    "timetable": RequiredUpload(form_name="Timetable structure", upload_status=upload_status.timetable,
                                                empty_form=forms.TimetableStructureUpload(),
                                                upload_url_name=UrlName.TIMETABLE_STRUCTURE_UPLOAD.value,
                                                reset_url_name=UrlName.TIMETABLE_STRUCTURE_RESET.value,
                                                example_download_absolute_url=ExampleFile.TIMETABLE.url),
                    "unsolved_classes": RequiredUpload(
                        form_name="Class requirements", upload_status=upload_status.unsolved_classes,
                        empty_form=forms.UnsolvedClassUpload(),
                        upload_url_name=UrlName.UNSOLVED_CLASSES_UPLOAD.value,
                        reset_url_name=UrlName.UNSOLVED_CLASSES_RESET.value,
                        example_download_absolute_url=ExampleFile.UNSOLVED_CLASS.url),
                    "fixed_classes": RequiredUpload(
                        form_name="Fixed classes", upload_status=upload_status.fixed_classes,
                        empty_form=forms.FixedClassUpload(),
                        upload_url_name=UrlName.FIXED_CLASSES_UPLOAD.value,
                        reset_url_name=UrlName.FIXED_CLASSES_RESET.value,
                        example_download_absolute_url=ExampleFile.FIXED_CLASS.url)
                    }
            }
        return context

    def post(self, request: http.HttpRequest, *args, **kwargs) -> http.HttpResponse:
        """
        POST requests to the data upload page's base URL should just be handled the same as GET requests.
        """
        return self.get(request=request, *args, **kwargs)
