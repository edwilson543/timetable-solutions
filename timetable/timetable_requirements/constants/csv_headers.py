"""Module listing the headers of the csv files used in the application"""

# Standard library imports
from dataclasses import dataclass
from typing import List


class Header:
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
    PERIOD_START_TIME = "period_start_time"
    PERIOD_DURATION = "period_duration"
    SUBJECT_NAME = "subject_name"
    TOTAL_SLOTS = "total_slots"
    MIN_SLOTS = "min_slots"

    # Headers in files containing many-to-many relationships
    PUPIL_IDS = "pupil_ids"
    SLOT_IDS = "slot_ids"


@dataclass(frozen=True)
class CSVFile:
    headers: List[str]
    id_column: str


@dataclass(frozen=True)
class CSVUplaodFiles:
    """Storage of the file structure of all csv files that get uploaded / downloaded from the database by users."""
    PUPILS = CSVFile(headers=[Header.PUPIL_ID, Header.FIRSTNAME, Header.SURNAME, Header.YEAR_GROUP],
                     id_column=Header.PUPIL_ID)
    TEACHERS = CSVFile(headers=[Header.TEACHER_ID, Header.FIRSTNAME, Header.SURNAME, Header.TITLE],
                       id_column=Header.TEACHER_ID)
    CLASSROOMS = CSVFile(headers=[Header.CLASSROOM_ID, Header.BUILDING, Header.ROOM_NUMBER],
                         id_column=Header.CLASSROOM_ID)
    TIMETABLE = CSVFile(headers=[Header.SLOT_ID, Header.DAY_OF_WEEK, Header.PERIOD_START_TIME, Header.PERIOD_DURATION],
                        id_column=Header.SLOT_ID)
    CLASS_REQUIREMENTS = CSVFile(headers=[Header.CLASS_ID, Header.SUBJECT_NAME, Header.TEACHER_ID, Header.PUPIL_IDS,
                                          Header.CLASSROOM_ID, Header.TOTAL_SLOTS, Header.MIN_SLOTS],
                                 id_column=Header.CLASS_ID)
    FIXED_CLASSES = CSVFile(headers=[Header.CLASS_ID, Header.SUBJECT_NAME, Header.TEACHER_ID, Header.PUPIL_IDS,
                                          Header.CLASSROOM_ID, Header.SLOT_IDS],
                            id_column=Header.CLASS_ID)
