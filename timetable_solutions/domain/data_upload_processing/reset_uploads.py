"""
Module defining the logic that allows users to reset their data uploads (i.e. delete the data they have already
uploaded)
"""

# Local application imports
from data import models


class ResetUploads:
    """
    Class to store which tables need resetting, and for which school, and do the resetting.
    Instantiated by various views, kept separate for cleanliness and to allow extendability.
    """
    def __init__(self,
                 school_access_key: int,
                 pupils: bool,
                 teachers: bool,
                 classrooms: bool,
                 timetable: bool,
                 lessons: bool):
    
        self._school_access_key = school_access_key
        
        # This data gets deleted only if they are passed as True to init
        self._pupils = pupils
        self._teachers = teachers
        self._classrooms = classrooms
        self._timetable = timetable
        
        # Note it doesn't make sense to persevere the Lesson table if any of the other tables are wiped
        self._lessons = pupils or teachers or classrooms or timetable or lessons

        self._reset_data()

    def _reset_data(self) -> None:
        """
        Function used to reset the school's data as relevant, depending on the dataclass field values.
        Note that the ORDER in which the models are deleted is very important.
        """
        if self._lessons:
            models.Lesson.delete_all_lessons_for_school(school_id=self._school_access_key)

        if self._pupils:
            models.Pupil.delete_all_instances_for_school(school_id=self._school_access_key)

        if self._teachers:
            models.Teacher.delete_all_instances_for_school(school_id=self._school_access_key)

        if self._classrooms:
            models.Classroom.delete_all_instances_for_school(school_id=self._school_access_key)

        if self._timetable:
            models.TimetableSlot.delete_all_instances_for_school(school_id=self._school_access_key)
