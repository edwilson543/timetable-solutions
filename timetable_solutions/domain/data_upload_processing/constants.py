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
    YEAR_GROUP = "year_group"
    PUPIL_ID = "pupil_id"
    TEACHER_ID = "teacher_id"
    CLASSROOM_ID = "classroom_id"
    SLOT_ID = "slot_id"
    LESSON_ID = "lesson_id"

    # Headers specific to individual files
    FIRSTNAME = "firstname"
    SURNAME = "surname"
    TITLE = "title"
    BUILDING = "building"
    ROOM_NUMBER = "room_number"
    DAY_OF_WEEK = "day_of_week"
    PERIOD_STARTS_AT = "period_starts_at"
    PERIOD_DURATION = "period_duration"
    SUBJECT_NAME = "subject_name"
    TOTAL_SLOTS = "total_required_slots"
    TOTAL_DOUBLES = "total_required_double_periods"

    # Headers in files containing many-to-many relationships
    PUPIL_IDS = "pupil_ids"
    USER_DEFINED_SLOTS = "user_defined_slot_ids"
    RELEVANT_YEAR_GROUPS = "relevant_year_groups"

    # Type reference - where pandas.read_csv() doesn't always get it right
    AMBIGUOUS_DTYPES = {
        YEAR_GROUP: str,
    }


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

    YEAR_GROUPS = FileStructure(
        headers=[Header.YEAR_GROUP], id_column=Header.YEAR_GROUP
    )
    PUPILS = FileStructure(
        headers=[Header.PUPIL_ID, Header.FIRSTNAME, Header.SURNAME, Header.YEAR_GROUP],
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
    TIMETABLE = FileStructure(
        headers=[
            Header.SLOT_ID,
            Header.DAY_OF_WEEK,
            Header.PERIOD_STARTS_AT,
            Header.PERIOD_DURATION,
            Header.RELEVANT_YEAR_GROUPS,
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

    @property
    def filepath(self) -> Path:
        """
        Property indicating the absolute path the example file is stored at on the local file system.
        """
        path = settings.BASE_DIR / settings.MEDIA_ROOT / "example_files" / self.value
        return path
