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


class UnsolvedClassReset(DataResetBase):
    """
    Class used to handle the resetting of pupil data.
    """
    unsolved_classes = True


class FixedClassReset(DataResetBase):
    """
    Class used to handle the resetting of pupil data.
    """
    fixed_classes = True
