"""
Module used to track the status of user data uploads into the database, and enforce any rules on which
uploads cannot yet be uploaded.
"""

# Standard library imports
from enum import StrEnum
from typing import Self

# Local application imports
from data import models


class UploadStatus(StrEnum):
    """
    Enumeration of the possible upload statuses that can apply to an individual file that the user needs to upload
    """
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    DISALLOWED = "disallowed"  # i.e. dependent on another file's completion status being complete, which is incomplete

    @classmethod
    def get_upload_status_from_bool(cls, upload_status: bool) -> Self:  # type: ignore
        """
        Method receiving an upload status as a boolean and returning it as an UploadStatus member value, to avoid
        doing the if/else chain below more than once
        """
        if upload_status:
            return cls.COMPLETE
        else:
            return cls.INCOMPLETE


class UploadStatusTracker:
    """
    Class used to store which files the user has successfully uploaded into the database, and any uploads that are
    currently disallowed.
    All instance attributes are stored as UploadStatus member values, however are passed to __init__ as booleans.
    """
    def __init__(self,
                 pupils: bool,
                 teachers: bool,
                 classrooms: bool,
                 timetable: bool,
                 lessons: bool):
        self.pupils = UploadStatus.get_upload_status_from_bool(upload_status=pupils).value  # type: ignore
        self.teachers = UploadStatus.get_upload_status_from_bool(upload_status=teachers).value  # type: ignore
        self.classrooms = UploadStatus.get_upload_status_from_bool(upload_status=classrooms).value  # type: ignore
        self.timetable = UploadStatus.get_upload_status_from_bool(upload_status=timetable).value  # type: ignore

        self.lessons = self._check_if_upload_allowed_then_get_status(class_upload_status=lessons).value

    def _check_if_upload_allowed_then_get_status(self, class_upload_status: bool) -> UploadStatus:
        """
        Method to get the upload status of the  uploads. If the user hasn't uploaded all the
        required tables that these tables reference, then we disallow these uploads until they have done.
        :return the uploads status of lessons, given an initial screening
        """
        able_to_add_class_data = (
                self.pupils == UploadStatus.COMPLETE.value and
                self.teachers == UploadStatus.COMPLETE.value and
                self.classrooms == UploadStatus.COMPLETE.value and
                self.timetable == UploadStatus.COMPLETE.value
        )
        if not able_to_add_class_data:
            return UploadStatus.DISALLOWED
        else:
            return UploadStatus.get_upload_status_from_bool(upload_status=class_upload_status)

    @classmethod
    def get_upload_status(cls, school: models.School) -> Self:  # type: ignore
        """
        Function querying the database to find out which files the user has uploaded,
        and return an UploadStatusTracker instance.
        """
        # Query database (by calling the data layer)
        pupil_upload_status = school.has_pupil_data
        teacher_upload_status = school.has_teacher_data
        classroom_upload_status = school.has_classroom_data
        timetable_upload_status = school.has_timetable_structure_data
        lesson_upload_status = school.has_lesson_data

        upload_status = cls(
            pupils=pupil_upload_status, teachers=teacher_upload_status, classrooms=classroom_upload_status,
            timetable=timetable_upload_status, lessons=lesson_upload_status
        )

        return upload_status

    @property
    def all_uploads_complete(self) -> bool:
        """
        Property that indicates whether a school has uploaded all the necessary files.
        This is used, for example, in the create timetables page, when deciding whether to render the full
        create_timetables page to users.
        """
        all_complete = (
                self.pupils == UploadStatus.COMPLETE.value and
                self.teachers == UploadStatus.COMPLETE.value and
                self.classrooms == UploadStatus.COMPLETE.value and
                self.timetable == UploadStatus.COMPLETE.value and
                self.lessons == UploadStatus.COMPLETE.value
        )
        return all_complete
