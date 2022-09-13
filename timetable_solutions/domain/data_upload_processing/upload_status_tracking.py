"""Module used to track the status of user data uploads into the database"""

# Standard library imports
from dataclasses import dataclass

# Local application imports
from data import models


@dataclass
class UploadStatus:
    """Dataclass used to store which files the user has successfully uploaded into the database"""
    PUPILS: bool
    TEACHERS: bool
    CLASSROOMS: bool
    TIMETABLE: bool
    UNSOLVED_CLASSES: bool
    FIXED_CLASSES: bool


def get_upload_status(school: models.School) -> UploadStatus:
    """
    Function querying the database to find out which files the user has uploaded, and return an UploadStatus instance
    """
    pupil_upload_status = school.has_pupil_data
    teacher_upload_status = school.has_teacher_data
    classroom_upload_status = school.has_classroom_data
    timetable_upload_status = school.has_timetable_structure_data
    unsolved_class_upload_status = school.has_unsolved_class_data
    fixed_class_upload_status = school.has_user_defined_fixed_class_data

    upload_status = UploadStatus(
        PUPILS=pupil_upload_status, TEACHERS=teacher_upload_status, CLASSROOMS=classroom_upload_status,
        TIMETABLE=timetable_upload_status, UNSOLVED_CLASSES=unsolved_class_upload_status,
        FIXED_CLASSES=fixed_class_upload_status)
    return upload_status
