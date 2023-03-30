"""
Convenience imports of all models.
Note that we also import the custom model managers to use as type hints when a function returns a queryset specifically
from that model.
"""

# Standard library imports
from typing import Union

from .break_ import Break, BreakQuerySet
from .classroom import Classroom, ClassroomQuerySet

# Exceptions
from .exceptions import SchoolMismatchError
from .lesson import Lesson, LessonQuerySet
from .pupil import Pupil, PupilQuerySet
from .school import School, SchoolQuerySet
from .teacher import Teacher, TeacherQuerySet
from .timetable_slot import TimetableSlot, TimetableSlotQuerySet
from .user_profile import Profile, ProfileQuerySet
from .year_group import YearGroup, YearGroupQuerySet

# Type hints
ModelSubclass = Union[
    Profile, School, YearGroup, Pupil, Teacher, Classroom, TimetableSlot, Lesson, Break
]
