"""
Base classes for the views used to handle different types of actions relating to the data upload page. These are:
    - DataUploadBase - base class for uploading data to the database
    - DataResetBase - base class for resetting a user's data
    - ExampleDownloadBase - base class for allowing the download of example upload files
The pattern is to implement all logic in these base classes, and then for each required upload, create one subclass
which has next to no code in it.
"""

# Standard library imports
from pathlib import Path
from typing import Callable, Type

# Django imports
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django import http
from django.views.generic import View
from django import urls

# Local application imports
from constants.url_names import UrlName
from data import models
from domain import data_upload_processing
from interfaces.data_upload import forms


class DataUploadBase(LoginRequiredMixin, View):
    """
    Base class for views handling the upload of a single file type to the database (via the post method).
    One subclass is declared per file type that the user needs to upload.
    Note - subclasses are used, rather than creating instances, since View.as_view(), used in the url
    dispatcher, is only available on classes and not on instances.

    :param file_structure - the column headers and id column of the uploaded file
    :param model - the model the uploaded file is seeking to create instances of
    :param form - the form that the view receives input from
    :param processor - the class that will be used to process the user's uploaded file into the database.
    """

    file_structure: data_upload_processing.FileStructure
    model: Type[models.ModelSubclass]
    form: Type[forms.FormSubclass]
    processor: Type[data_upload_processing.Processor]

    @staticmethod
    def get() -> http.HttpResponseRedirect:
        """
        Method to redirect users accessing the endpoints directly to data upload page.
        """
        return http.HttpResponseRedirect(urls.reverse(UrlName.FILE_UPLOAD_PAGE.value))

    def post(self, request: http.HttpRequest) -> http.HttpResponseRedirect:
        """
        All subclasses of this View upload a single file, which this post method handles.
        If the upload is successful, the remaining empty forms are displayed, otherwise the error messages are shown.
        """
        form = self.form(request.POST, request.FILES)
        school_access_key = request.user.profile.school.school_access_key
        if form.is_valid():
            file = request.FILES[self.form.Meta.file_field_name]
            upload_processor = self.processor(
                school_access_key=school_access_key,
                model=self.model,
                csv_file=file,
                csv_headers=self.file_structure.headers,
                id_column_name=self.file_structure.id_column,
            )

            # Create a flash message
            if upload_processor.upload_error_message is not None:
                messages.add_message(
                    request,
                    level=messages.ERROR,
                    message=upload_processor.upload_error_message,
                )
            elif upload_processor.upload_successful:
                message = (
                    f"Successfully saved your data for {upload_processor.n_model_instances_created} "
                    f"{self.model.Constant.human_string_plural}!"
                )
                messages.add_message(request, level=messages.SUCCESS, message=message)
            else:
                # Added insurance, in case the file upload processor hasn't uploaded, or made an error message
                message = "Could not read data from file. Please check it matches the example file and try again."
                messages.add_message(request, level=messages.ERROR, message=message)

        return http.HttpResponseRedirect(urls.reverse(UrlName.FILE_UPLOAD_PAGE.value))


class DataResetBase(LoginRequiredMixin, View):
    """
    Base class for views handling the reset data buttons provided on the data reset page.
    The class attributes are aliases for the database tables which reset by this view - each subclass sets exactly
    one of these to True, except the subclass which resets all the data tables in one go.

    The domain layer handles any dependency-related resets.
    """

    year_groups: bool = False
    pupils: bool = False
    teachers: bool = False
    classrooms: bool = False
    timetable: bool = False
    lessons: bool = False

    @staticmethod
    def get() -> http.HttpResponseRedirect:
        """
        Method to redirect users accessing the endpoints directly to data upload page.
        """
        return http.HttpResponseRedirect(urls.reverse(UrlName.FILE_UPLOAD_PAGE.value))

    def post(self, request: http.HttpRequest) -> http.HttpResponseRedirect:
        """
        Post method to carry out the resetting of the user's data.
        We use the ResetUploads class to allow extendability of the reset logic without ending up with an enormous
        view, and to keep the HTTP handling / domain-focused logic distinct
        """
        school_access_key = request.user.profile.school.school_access_key

        data_upload_processing.ResetUploads(
            school_access_key=school_access_key,
            year_groups=self.year_groups,
            pupils=self.pupils,
            teachers=self.teachers,
            classrooms=self.classrooms,
            timetable=self.timetable,
            lessons=self.lessons,
        )

        return http.HttpResponseRedirect(urls.reverse(UrlName.FILE_UPLOAD_PAGE.value))


class ExampleDownloadBase(LoginRequiredMixin):
    """
    Class responsible for allowing users to download the example files
    """

    example_filepath: Path  # Absolute path in the local filesystem to the file to download

    @classmethod
    def as_view(cls) -> Callable:
        """
        as_view is used to keep a clean interface with the other views in the url dispatcher
        """
        return cls._view

    @classmethod
    def _view(cls, request: http.HttpRequest) -> http.FileResponse:
        """
        Method to instantiate and return a file response object, using the example_filepath class attribute.
        """
        del request  # request is not used, but must be included as an argument
        response = http.FileResponse(
            open(cls.example_filepath, "rb"), as_attachment=True
        )
        return response
