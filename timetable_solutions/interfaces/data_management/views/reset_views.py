"""
Views relating to the resetting of user uploaded data.
 - Each subclass of DataResetBase handles the upload of one OR MORE of the user's uploads.
"""

# Local application imports
from .base_classes import DataResetBase


class PupilListReset(DataResetBase):
    """
    Class used to handle the resetting of pupil data.
    """

    pupils = True


class TeacherListReset(DataResetBase):
    """
    Class used to handle the resetting of teacher data.
    """

    teachers = True


class ClassroomListReset(DataResetBase):
    """
    Class used to handle the resetting of classroom data.
    """

    classrooms = True


class TimetableStructureReset(DataResetBase):
    """
    Class used to handle the resetting of timetable data.
    """

    timetable = True


class YearGroupReset(DataResetBase):
    """
    Class used to handle the resetting of year_group data.
    """

    year_groups = True


class LessonReset(DataResetBase):
    """
    Class used to handle the resetting of lesson data.
    """

    lessons = True


class BreakReset(DataResetBase):
    """
    Class used to handle the resetting of break data.
    """

    breaks = True


class AllSchoolDataReset(DataResetBase):
    """
    Class used to reset ALL the data relevant to a given school (except users / the school itself)
    """

    teachers = True
    classrooms = True
    year_groups = True
    pupils = True
    timetable = True
    lessons = True
