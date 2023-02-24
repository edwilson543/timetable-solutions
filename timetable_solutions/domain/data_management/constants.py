"""
Module listing constants related to the processing of uploaded user files.
"""


# Standard library imports
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

# Django imports
from django.conf import settings


class Header:
    """
    Class storing string literals that are header of upload files that must be recognised by the file upload processor
    """

    # Misc.
    SCHOOL_ID = "school_id"

    # Id columns
    BREAK_ID = "break_id"
    CLASSROOM_ID = "classroom_id"
    LESSON_ID = "lesson_id"
    PUPIL_ID = "pupil_id"
    SLOT_ID = "slot_id"
    TEACHER_ID = "teacher_id"
    YEAR_GROUP_ID = "year_group_id"

    # Headers specific to individual files
    BREAK_NAME = "break_name"
    BUILDING = "building"
    DAY_OF_WEEK = "day_of_week"
    STARTS_AT = "starts_at"
    ENDS_AT = "ends_at"
    FIRSTNAME = "firstname"
    ROOM_NUMBER = "room_number"
    SUBJECT_NAME = "subject_name"
    SURNAME = "surname"
    TITLE = "title"
    TOTAL_DOUBLES = "total_required_double_periods"
    TOTAL_SLOTS = "total_required_slots"
    YEAR_GROUP_NAME = "year_group_name"

    # Headers in files containing many-to-many relationships
    PUPIL_IDS = "pupil_ids"
    TEACHER_IDS = "teacher_ids"
    RELEVANT_YEAR_GROUP_IDS = "relevant_year_group_ids"
    USER_DEFINED_SLOTS = "user_defined_slot_ids"


@dataclass(frozen=True)
class FileStructure:
    """
    Parameterisation of the structure of each user uploaded file
    """

    headers: list[str]
    id_column: str


@dataclass(frozen=True)
class UploadFileStructure:
    """
    Storage of the file structure of all csv files that get uploaded / downloaded from the database by users.
    """

    PUPILS = FileStructure(
        headers=[
            Header.PUPIL_ID,
            Header.FIRSTNAME,
            Header.SURNAME,
            Header.YEAR_GROUP_ID,
        ],
        id_column=Header.PUPIL_ID,
    )
    TEACHERS = FileStructure(
        headers=[Header.TEACHER_ID, Header.FIRSTNAME, Header.SURNAME, Header.TITLE],
        id_column=Header.TEACHER_ID,
    )
    CLASSROOMS = FileStructure(
        headers=[Header.CLASSROOM_ID, Header.BUILDING, Header.ROOM_NUMBER],
        id_column=Header.CLASSROOM_ID,
    )
    YEAR_GROUPS = FileStructure(
        headers=[Header.YEAR_GROUP_ID, Header.YEAR_GROUP_NAME],
        id_column=Header.YEAR_GROUP_ID,
    )

    # Files with relations
    TIMETABLE = FileStructure(
        headers=[
            Header.SLOT_ID,
            Header.DAY_OF_WEEK,
            Header.STARTS_AT,
            Header.ENDS_AT,
            Header.RELEVANT_YEAR_GROUP_IDS,
        ],
        id_column=Header.SLOT_ID,
    )
    LESSON = FileStructure(
        headers=[
            Header.LESSON_ID,
            Header.SUBJECT_NAME,
            Header.TEACHER_ID,
            Header.PUPIL_IDS,
            Header.CLASSROOM_ID,
            Header.TOTAL_SLOTS,
            Header.TOTAL_DOUBLES,
            Header.USER_DEFINED_SLOTS,
        ],
        id_column=Header.LESSON_ID,
    )
    BREAK = FileStructure(
        headers=[
            Header.BREAK_ID,
            Header.BREAK_NAME,
            Header.DAY_OF_WEEK,
            Header.STARTS_AT,
            Header.ENDS_AT,
            Header.TEACHER_IDS,
            Header.RELEVANT_YEAR_GROUP_IDS,
        ],
        id_column=Header.BREAK_ID,
    )


class ExampleFile(StrEnum):
    """
    Enumeration of all the example files that can be downloaded by users, and construction of their respective urls.
    """

    YEAR_GROUPS = "example_year_groups.csv"
    PUPILS = "example_pupils.csv"
    TEACHERS = "example_teachers.csv"
    CLASSROOMS = "example_classrooms.csv"
    TIMETABLE = "example_timetable.csv"
    LESSON = "example_lessons.csv"
    BREAK = "example_breaks.csv"

    @property
    def filepath(self) -> Path:
        """
        Property indicating the absolute path the example file is stored at on the local file system.
        """
        path = settings.BASE_DIR / settings.MEDIA_ROOT / "example_files" / self.value
        return path


class DataStatus(StrEnum):
    """The possible statuses of a user's data with respect to a single model."""

    # School has some data for this model
    NOT_EMPTY = "not-empty"

    # School can but has not yet added any data for this model
    EMPTY = "empty"

    # This model cannot be populated before another model which is currently EMPTY or DISALLOWED
    DISALLOWED = "disallowed"
