"""
Module listing constants related to the processing of uploaded user files.
"""

# Standard library imports
from dataclasses import dataclass
from typing import List


class Header:
    """
    Class storing string literals that are header of upload files that must be recognised by the file upload processor
    """
    # Misc.
    SCHOOL_ID = "school_id"

    # Id columns
    PUPIL_ID = "pupil_id"
    TEACHER_ID = "teacher_id"
    CLASSROOM_ID = "classroom_id"
    SLOT_ID = "slot_id"
    CLASS_ID = "class_id"

    # Headers specific to individual files
    FIRSTNAME = "firstname"
    SURNAME = "surname"
    TITLE = "title"
    YEAR_GROUP = "year_group"
    BUILDING = "building"
    ROOM_NUMBER = "room_number"
    DAY_OF_WEEK = "day_of_week"
    PERIOD_STARTS_AT = "period_starts_at"
    PERIOD_DURATION = "period_duration"
    SUBJECT_NAME = "subject_name"
    TOTAL_SLOTS = "total_slots"
    N_DOUBLE_PERIODS = "n_double_periods"

    # Headers in files containing many-to-many relationships
    PUPIL_IDS = "pupil_ids"
    SLOT_IDS = "slot_ids"


@dataclass(frozen=True)
class FileStructure:
    """
    Parameterisation of the structure of each user uploaded file
    """
    headers: List[str]
    id_column: str


@dataclass(frozen=True)
class UploadFileStructure:
    """
    Storage of the file structure of all csv files that get uploaded / downloaded from the database by users.
    """
    PUPILS = FileStructure(headers=[Header.PUPIL_ID, Header.FIRSTNAME, Header.SURNAME, Header.YEAR_GROUP],
                           id_column=Header.PUPIL_ID)
    TEACHERS = FileStructure(headers=[Header.TEACHER_ID, Header.FIRSTNAME, Header.SURNAME, Header.TITLE],
                             id_column=Header.TEACHER_ID)
    CLASSROOMS = FileStructure(headers=[Header.CLASSROOM_ID, Header.BUILDING, Header.ROOM_NUMBER],
                               id_column=Header.CLASSROOM_ID)
    TIMETABLE = FileStructure(
        headers=[Header.SLOT_ID, Header.DAY_OF_WEEK, Header.PERIOD_STARTS_AT, Header.PERIOD_DURATION],
        id_column=Header.SLOT_ID)
    UNSOLVED_CLASSES = FileStructure(headers=[Header.CLASS_ID, Header.SUBJECT_NAME, Header.TEACHER_ID, Header.PUPIL_IDS,
                                              Header.CLASSROOM_ID, Header.TOTAL_SLOTS, Header.N_DOUBLE_PERIODS],
                                     id_column=Header.CLASS_ID)
    FIXED_CLASSES = FileStructure(headers=[Header.CLASS_ID, Header.SUBJECT_NAME, Header.TEACHER_ID, Header.PUPIL_IDS,
                                           Header.CLASSROOM_ID, Header.SLOT_IDS], id_column=Header.CLASS_ID)
