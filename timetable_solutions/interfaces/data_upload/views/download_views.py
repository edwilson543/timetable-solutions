"""
Views responsible for allowing users to download the example upload files.
All views just return a FileResponse, containing the requested file.
"""

# Local application imports
from .base_classes import ExampleDownloadBase
from domain.data_upload_processing.constants import ExampleFile


class TeacherDownload(ExampleDownloadBase):
    """
    Class used to download the example teachers file.
    """

    example_filepath = ExampleFile.TEACHERS.filepath


class ClassroomDownload(ExampleDownloadBase):
    """
    Class used to download the example classrooms file.
    """

    example_filepath = ExampleFile.CLASSROOMS.filepath


class YearGroupDownload(ExampleDownloadBase):
    """
    Class used to download the example year groups file.
    """

    example_filepath = ExampleFile.YEAR_GROUPS.filepath


class PupilDownload(ExampleDownloadBase):
    """
    Class used to download the example pupils file.
    """

    example_filepath = ExampleFile.PUPILS.filepath


class TimetableDownload(ExampleDownloadBase):
    """
    Class used to download the example timetable file.
    """

    example_filepath = ExampleFile.TIMETABLE.filepath


class LessonDownload(ExampleDownloadBase):
    """
    Class used to download the example lessons file.
    """

    example_filepath = ExampleFile.LESSON.filepath
