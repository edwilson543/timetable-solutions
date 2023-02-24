"""
Module used to track the status of user data uploads into the database, and enforce any rules on which
uploads cannot yet be uploaded.
"""


# Standard library imports
from dataclasses import dataclass
from enum import StrEnum

# Local application imports
from data import models


class UploadStatus(StrEnum):
    """
    Enumeration of the possible upload statuses that can apply to an individual file that the user needs to upload
    """

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    DISALLOWED = "disallowed"  # i.e. dependent on another file's completion status being complete, which is incomplete


@dataclass(frozen=True)
class UploadStatusReason:
    """Dataclass to store an upload status alongside a reason for this status, if necessary"""

    status: "UploadStatus"
    reason: str | None = None  # Only not None if upload status

    @classmethod
    def get_status_from_bool(cls, upload_status: bool) -> "UploadStatusReason":
        """
        Method receiving an upload status as a boolean and returning it as an UploadStatus member value, to avoid
        using the if/else chain more than once
        """
        if upload_status:
            return cls(status=UploadStatus.COMPLETE)
        else:
            return cls(status=UploadStatus.INCOMPLETE)


class UploadStatusTracker:
    """
    Class used to store which files the user has successfully uploaded into the database, and any uploads that are
    currently disallowed.
    """

    year_groups: UploadStatusReason
    teachers: UploadStatusReason
    classrooms: UploadStatusReason
    pupils: UploadStatusReason
    timetable: UploadStatusReason
    lessons: UploadStatusReason
    breaks: UploadStatusReason

    @classmethod
    def get_upload_status(cls, school: models.School) -> "UploadStatusTracker":
        """
        Function querying the database to find out which files the user has uploaded,
        and return an UploadStatusTracker instance.
        """
        # Query database (by calling the data layer)
        year_group_status = school.has_year_group_data
        pupil_upload_status = school.has_pupil_data
        teacher_upload_status = school.has_teacher_data
        classroom_upload_status = school.has_classroom_data
        timetable_upload_status = school.has_timetable_structure_data
        lesson_upload_status = school.has_lesson_data
        break_upload_status = school.has_break_data

        upload_status = cls(
            year_groups=year_group_status,
            pupils=pupil_upload_status,
            teachers=teacher_upload_status,
            classrooms=classroom_upload_status,
            timetable=timetable_upload_status,
            lessons=lesson_upload_status,
            breaks=break_upload_status,
        )

        return upload_status

    def __init__(
        self,
        year_groups: bool,
        teachers: bool,
        classrooms: bool,
        pupils: bool,
        timetable: bool,
        lessons: bool,
        breaks: bool,
    ):
        """
        At initialisation the boolean parameters are converted to UploadStatusReasons
        """
        self._set_upload_status(
            year_groups=year_groups,
            teachers=teachers,
            classrooms=classrooms,
            pupils=pupils,
            timetable=timetable,
            lessons=lessons,
            breaks=breaks,
        )

    def _set_upload_status(
        self,
        year_groups: bool,
        teachers: bool,
        classrooms: bool,
        pupils: bool,
        timetable: bool,
        lessons: bool,
        breaks: bool,
    ) -> None:
        """
        Method to set the instance attributes on an UploadStatusTracker instance, given all the relevant bools.
        """
        # Independent uploads
        self.year_groups = UploadStatusReason.get_status_from_bool(
            upload_status=year_groups
        )
        self.teachers = UploadStatusReason.get_status_from_bool(upload_status=teachers)
        self.classrooms = UploadStatusReason.get_status_from_bool(
            upload_status=classrooms
        )

        # Year group dependent uploads
        self.pupils = self._get_year_group_dependent_upload_status(
            target_file_status=pupils
        )
        self.timetable = self._get_year_group_dependent_upload_status(
            target_file_status=timetable
        )

        # Dependent on other uploads
        self.breaks = self._get_break_upload_status(break_upload_status=breaks)
        self.lessons = self._get_lesson_upload_status(lesson_upload_status=lessons)

    def _get_year_group_dependent_upload_status(
        self, target_file_status: bool
    ) -> UploadStatusReason:
        """
        Get the upload status of a file that requires the year group file to be uploaded first
        :param target_file_status - the file we want to get the status of.
        """
        if not self.year_groups.status == UploadStatus.COMPLETE:
            reason = (
                "You must define your year groups before this file can be uploaded."
            )
            return UploadStatusReason(status=UploadStatus.DISALLOWED, reason=reason)
        else:
            return UploadStatusReason.get_status_from_bool(
                upload_status=target_file_status
            )

    # Methods checking dependent uploads status
    def _get_lesson_upload_status(
        self, lesson_upload_status: bool
    ) -> UploadStatusReason:
        """
        Get the upload status of the lesson file (which may be disallowed).
        If the user hasn't uploaded all the required tables that the Lesson model references,
        then we disallow these uploads until they have done.
        """
        able_to_add_lesson_data = (
            self.year_groups.status == UploadStatus.COMPLETE
            and self.pupils.status == UploadStatus.COMPLETE
            and self.teachers.status == UploadStatus.COMPLETE
            and self.classrooms.status == UploadStatus.COMPLETE
            and self.timetable.status == UploadStatus.COMPLETE
        )

        if not able_to_add_lesson_data:
            reason = "All other files must be uploaded before this file can be."
            return UploadStatusReason(status=UploadStatus.DISALLOWED, reason=reason)
        else:
            return UploadStatusReason.get_status_from_bool(
                upload_status=lesson_upload_status
            )

    def _get_break_upload_status(self, break_upload_status: bool) -> UploadStatusReason:
        able_to_add_break_data = (
            self.year_groups.status == UploadStatus.COMPLETE
            and self.teachers.status == UploadStatus.COMPLETE
        )

        if not able_to_add_break_data:
            reason = "Year group and teacher data must be set first."
            return UploadStatusReason(status=UploadStatus.DISALLOWED, reason=reason)
        else:
            return UploadStatusReason.get_status_from_bool(
                upload_status=break_upload_status
            )

    # PROPERTIES
    @property
    def all_uploads_complete(self) -> bool:
        """
        Property that indicates whether a school has uploaded all the necessary files.
        This is used, for example, in the create timetables page, when deciding whether to render the full
        create_timetables page to users.
        """
        all_complete = (
            self.year_groups.status == UploadStatus.COMPLETE
            and self.pupils.status == UploadStatus.COMPLETE
            and self.teachers.status == UploadStatus.COMPLETE
            and self.classrooms.status == UploadStatus.COMPLETE
            and self.timetable.status == UploadStatus.COMPLETE
            and self.lessons.status == UploadStatus.COMPLETE
            and self.breaks.status == UploadStatus.COMPLETE
        )
        return all_complete
