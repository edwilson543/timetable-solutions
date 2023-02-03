"""
Module defining the data upload page, its context, and required ancillaries.
"""

# Standard library imports
from dataclasses import dataclass
from typing import Any, TypedDict

# Django imports
from django import urls, http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView

# Local application imports
from interfaces.constants import UrlName
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
    upload_status: data_upload_processing.UploadStatusReason
    empty_form: forms.UploadForm
    upload_url_name: UrlName
    reset_url_name: UrlName
    example_download_url_name: UrlName
    reset_warning: data_upload_processing.ResetWarning


class RequiredFormsContext(TypedDict):
    """
    Type and structure of the required_forms context provided to the UploadPage.
    """

    teachers: RequiredUpload
    classrooms: RequiredUpload
    year_groups: RequiredUpload
    pupils: RequiredUpload
    timetable: RequiredUpload
    lessons: RequiredUpload
    breaks: RequiredUpload


class UploadPageContext(TypedDict):
    """
    Type and structure of the context provided to the data upload page.
    """

    required_forms: RequiredFormsContext


class UploadPage(LoginRequiredMixin, TemplateView):
    """
    Template view with the following main purposes:
        - Handling HTTP to the base data upload page (whose url this class is attached to)
        - Defining the logic for gathering all the required upload forms into one set of context data
        - Being subclassed, to provide its rendering of the data upload page (with the full context) to other views.
    """

    login_url = urls.reverse_lazy("login")
    template_name = "file_upload.html"

    def get_context_data(self, *args: Any, **kwargs: Any) -> UploadPageContext:
        """
        Method to get a dictionary of 'RequiredUpload' instances which are used to then control the rendering of either
        an empty form, or a completion message.

        Note the context also provides several url names for reversing in the template tags.
        """
        school = self.request.user.profile.school
        upload_status = data_upload_processing.UploadStatusTracker.get_upload_status(
            school=school
        )

        if upload_status.all_uploads_complete:
            message = (
                "You have uploaded all the required files, and can now start generating timetable solutions!\n"
                f"Navigate over to the "
                f"<a href='{urls.reverse(UrlName.CREATE_TIMETABLES.value)}'>create</a> page to get started."
            )
            messages.add_message(
                request=self.request,
                level=messages.INFO,
                message=message,
                extra_tags="safe",
            )

        context: UploadPageContext = {
            "required_forms": {
                "teachers": RequiredUpload(
                    form_name="Teachers",
                    upload_status=upload_status.teachers,
                    empty_form=forms.TeacherListUpload(),
                    upload_url_name=UrlName.TEACHER_LIST_UPLOAD,
                    reset_url_name=UrlName.TEACHER_LIST_RESET,
                    example_download_url_name=UrlName.TEACHER_DOWNLOAD,
                    reset_warning=data_upload_processing.ResetWarning.teachers,
                ),
                "classrooms": RequiredUpload(
                    form_name="Classrooms",
                    upload_status=upload_status.classrooms,
                    empty_form=forms.ClassroomListUpload(),
                    upload_url_name=UrlName.CLASSROOM_LIST_UPLOAD,
                    reset_url_name=UrlName.CLASSROOM_LIST_RESET,
                    example_download_url_name=UrlName.CLASSROOM_DOWNLOAD,
                    reset_warning=data_upload_processing.ResetWarning.classrooms,
                ),
                "year_groups": RequiredUpload(
                    form_name="Year Groups",
                    upload_status=upload_status.year_groups,
                    empty_form=forms.YearGroupUpload(),
                    upload_url_name=UrlName.YEAR_GROUP_UPLOAD,
                    reset_url_name=UrlName.YEAR_GROUP_RESET,
                    example_download_url_name=UrlName.YEAR_GROUP_DOWNLOAD,
                    reset_warning=data_upload_processing.ResetWarning.year_groups,
                ),
                "breaks": RequiredUpload(
                    form_name="Break times",
                    upload_status=upload_status.breaks,
                    empty_form=forms.BreakUpload(),
                    upload_url_name=UrlName.BREAKS_UPLOAD,
                    reset_url_name=UrlName.BREAKS_RESET,
                    example_download_url_name=UrlName.BREAKS_DOWNLOAD,
                    reset_warning=data_upload_processing.ResetWarning.breaks,
                ),
                "pupils": RequiredUpload(
                    form_name="Pupils",
                    upload_status=upload_status.pupils,
                    empty_form=forms.PupilListUpload(),
                    upload_url_name=UrlName.PUPIL_LIST_UPLOAD,
                    reset_url_name=UrlName.PUPIL_LIST_RESET,
                    example_download_url_name=UrlName.PUPIL_DOWNLOAD,
                    reset_warning=data_upload_processing.ResetWarning.pupils,
                ),
                "timetable": RequiredUpload(
                    form_name="Timetable structure",
                    upload_status=upload_status.timetable,
                    empty_form=forms.TimetableStructureUpload(),
                    upload_url_name=UrlName.TIMETABLE_STRUCTURE_UPLOAD,
                    reset_url_name=UrlName.TIMETABLE_STRUCTURE_RESET,
                    example_download_url_name=UrlName.TIMETABLE_DOWNLOAD,
                    reset_warning=data_upload_processing.ResetWarning.timetable,
                ),
                "lessons": RequiredUpload(
                    form_name="Lessons",
                    upload_status=upload_status.lessons,
                    empty_form=forms.LessonUpload(),
                    upload_url_name=UrlName.LESSONS_UPLOAD,
                    reset_url_name=UrlName.LESSONS_RESET,
                    example_download_url_name=UrlName.LESSONS_DOWNLOAD,
                    reset_warning=data_upload_processing.ResetWarning.lessons,
                ),
            }
        }
        return context

    def post(
        self, request: http.HttpRequest, *args: Any, **kwargs: Any
    ) -> http.HttpResponse:
        """
        POST requests to the data upload page's base URL should just be handled the same as GET requests.
        """
        return self.get(request=request, *args, **kwargs)
