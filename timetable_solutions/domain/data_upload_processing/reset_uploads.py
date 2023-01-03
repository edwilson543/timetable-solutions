"""
Module defining the logic that allows users to reset their data uploads (i.e. delete the data they have already
uploaded)
"""

# Standard library imports
from enum import StrEnum

# Local application imports
from data import models


class ResetUploads:
    """
    Class to store which tables need resetting, and for which school, and do the resetting.
    Instantiated by various views, kept separate for cleanliness and to allow extendability.
    """

    def __init__(
        self,
        school_access_key: int,
        classrooms: bool,
        teachers: bool,
        timetable: bool,
        year_groups: bool,
        pupils: bool,
        lessons: bool,
    ):

        self._school_access_key = school_access_key

        # This data gets deleted only if they are passed as True to init
        self._classrooms = classrooms
        self._teachers = teachers
        self._year_groups = year_groups

        # This data needs resetting if the year groups get wiped
        self._pupils = pupils or year_groups
        self._timetable = timetable or year_groups

        # Lesson needs resetting if any of the other tables are wiped
        self._lessons = (
            year_groups or pupils or teachers or classrooms or timetable or lessons
        )

        self._reset_data()

    def _reset_data(self) -> None:
        """
        Function used to reset the school's data as relevant, depending on the dataclass field values.
        Note that the ORDER in which the models are deleted is very important.
        """
        # Lesson instances must be deleted first, due to foreign key protection constraints...
        if self._lessons:
            models.Lesson.delete_all_lessons_for_school(
                school_id=self._school_access_key
            )

        # ... closely followed by YearGroup instances, for the same reason
        if self._year_groups:
            models.YearGroup.delete_all_instances_for_school(
                school_id=self._school_access_key
            )

        if self._pupils:
            models.Pupil.delete_all_instances_for_school(
                school_id=self._school_access_key
            )

        if self._teachers:
            models.Teacher.delete_all_instances_for_school(
                school_id=self._school_access_key
            )

        if self._classrooms:
            models.Classroom.delete_all_instances_for_school(
                school_id=self._school_access_key
            )

        if self._timetable:
            models.TimetableSlot.delete_all_instances_for_school(
                school_id=self._school_access_key
            )


class ResetWarning(StrEnum):
    """
    Mapping of reset file to the warning message displayed to users for the file(s) it will reset.
    """

    teachers = "This will reset all of your teacher data, are you sure?"
    classrooms = "This will reset all of your classroom data, are you sure?"
    year_groups = "This will reset all of your year group, pupil and timetable structure data, are you sure?"
    pupils = "This will reset all of your pupil data, are you sure?"
    timetable = "This will reset all of your timetable structure data, are you sure?"
    lessons = "This will reset ALL of your uploaded data, are you sure?"
