"""
A separate view is used for each file that gets uploaded, since they are uploaded separately.
These views are virtually identical, and thus can just be instances of some generic view class.
This module defines that generic view class, and its ancillaries.
"""

# Standard library imports
from dataclasses import dataclass
from typing import Dict, Type

# Django imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.http import HttpRequest, HttpResponse
from django.template import loader
from django import views
from django import urls

# Local application imports
from constants.url_names import UrlName
from data.utils import ModelSubclass
from domain import data_upload_processing
from interfaces.data_upload import forms


@dataclass
class RequiredUpload:
    """
    Dataclass to store information relating to each form, used to decide whether to render an empty instance of that
    form in the template, or instead to render some message indicating that the data has already been uploaded.
    """
    form_name: str
    upload_status: str | bool
    empty_form: forms.Form
    url_name: UrlName

    def __post_init__(self):
        """Reset upload status to a string which is more easily rendered in the template, without unnecessary tags."""
        if self.upload_status:
            self.upload_status = "Complete"
        else:
            self.upload_status = "Incomplete"


def _get_all_form_context(request: HttpRequest) -> Dict:
    """
    Function to get a dictionary of 'RequiredUpload' instances - these are used to then control the rendering of either
    the empty form, or a completion message.
    """
    # We retrieve the upload status of each of the necessary datasets for the given school
    # noinspection PyUnresolvedReferences
    school = request.user.profile.school
    upload_status = data_upload_processing.get_upload_status(school=school)

    context = {"required_forms":
               {
                   "teachers": RequiredUpload(form_name="Teacher list", upload_status=upload_status.TEACHERS,
                                              empty_form=forms.TeacherListUpload(),
                                              url_name=UrlName.TEACHER_LIST_UPLOAD.value),
                   "pupils": RequiredUpload(form_name="Pupil List", upload_status=upload_status.PUPILS,
                                            empty_form=forms.PupilListUpload(),
                                            url_name=UrlName.PUPIL_LIST_UPLOAD.value),
                   "classrooms": RequiredUpload(form_name="Classroom List", upload_status=upload_status.CLASSROOMS,
                                                empty_form=forms.ClassroomListUpload(),
                                                url_name=UrlName.CLASSROOM_LIST_UPLOAD.value),
                   "timetable": RequiredUpload(form_name="Timetable Structure", upload_status=upload_status.TIMETABLE,
                                               empty_form=forms.TimetableStructureUpload(),
                                               url_name=UrlName.TIMETABLE_STRUCTURE_UPLOAD.value),
                   "unsolved_classes": RequiredUpload(
                       form_name="Class requirements", upload_status=upload_status.UNSOLVED_CLASSES,
                       empty_form=forms.UnsolvedClassUpload(), url_name=UrlName.UNSOLVED_CLASSES_UPLOAD.value),
                   "fixed_classes": RequiredUpload(
                       form_name="Fixed classes", upload_status=upload_status.FIXED_CLASSES,
                       empty_form=forms.FixedClassUpload(), url_name=UrlName.FIXED_CLASSES_UPLOAD.value)
               }
               }
    return context


@login_required
def upload_page_view(request, error_message: str | None = None):
    """
    View called by the individual views for each of the form upload views.
    This is then used in the POST method of the generic view class.
    """
    template = loader.get_template("file_upload.html")
    context = _get_all_form_context(request=request)
    context["error_message"] = error_message
    return HttpResponse(template.render(context, request))


class DataUploadView(LoginRequiredMixin, views.View):
    login_url = urls.reverse_lazy("login")

    def __init__(self,
                 file_structure: data_upload_processing.FileStructure,
                 model: Type[ModelSubclass],
                 form: Type[forms.FormSubclass],
                 is_fixed_class_upload_view: bool = False,
                 is_unsolved_class_upload_view: bool = False):
        """
        Base view class for the upload of a single file to the database. One subclass is create per file that gets
        uploaded. The class is subclasses, rather than creating instances, since View.as_view(), used in the url
        dispatcher, is only available on classes and not on instances.

        :param file_structure - the column headers and id column of the uploaded file
        :param model - the model the uploaded file is seeking to create instances of
        :param form - the form that the view receives input from
        :param is_unsolved_class_upload_view & is_fixed_class_upload_view - boolean values handling special cases
        requiring different processing of the user uploaded file
        """
        super().__init__()
        self._file_structure = file_structure
        self._model = model
        self._form = form
        self._is_fixed_class_upload_view = is_fixed_class_upload_view
        self._is_unsolved_class_upload_view = is_unsolved_class_upload_view
        self.error_message = None

    @staticmethod
    def get(request, *arg, **kwarg):
        """
        If the user accesses the class' url directly, we use the upload page view to render the upload data form.
        """
        return upload_page_view(request)

    def post(self, request, *args, **kwargs):
        """
        All instances of the subclasses of this View upload a single file, which this post method handles.
        If the upload is successful, the remaining empty forms are displayed, otherwise the error messages are shown.
        """
        form = self._form(request.POST, request.FILES)
        school_access_key = request.user.profile.school.school_access_key
        if form.is_valid():
            file = request.FILES[self._form.Meta.file_field_name]
            upload_processor = data_upload_processing.FileUploadProcessor(
                csv_file=file, csv_headers=self._file_structure.headers, id_column_name=self._file_structure.id_column,
                model=self._model, school_access_key=school_access_key,
                is_fixed_class_upload=self._is_fixed_class_upload_view,
                is_unsolved_class_upload=self._is_unsolved_class_upload_view
            )
            self.error_message = upload_processor.upload_error_message  # Will just be None if no errors

        return upload_page_view(request, self.error_message)
