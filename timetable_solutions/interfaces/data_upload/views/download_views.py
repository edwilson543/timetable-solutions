"""
Views responsible for allowing users to download the example upload files.
All views just return a FileResponse, containing the requested file.
"""

# Local application imports
from .base_classes import ExampleDownloadBase
from constants.example_files import ExampleFile


class PupilDownload(ExampleDownloadBase):
    """
    Class used to download the example pupils file.
    """
    example_filepath = ExampleFile.PUPILS.filepath


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


class TimetableDownload(ExampleDownloadBase):
    """
    Class used to download the example timetable file.
    """
    example_filepath = ExampleFile.TIMETABLE.filepath


class UnsolvedClassDownload(ExampleDownloadBase):
    """
    Class used to download the example unsolved class file.
    """
    example_filepath = ExampleFile.UNSOLVED_CLASS.filepath


class FixedClassDownload(ExampleDownloadBase):
    """
    Class used to download the example pupils file.
    """
    example_filepath = ExampleFile.FIXED_CLASS.filepath
