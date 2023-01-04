"""
Convenience imports of all models.
Note that we also import the custom model managers to use as type hints when a function returns a queryset specifically
from that model.
"""
from typing import Union

from .user_profile import Profile, ProfileQuerySet, UserRole
from .school import School, SchoolQuerySet
from .year_group import YearGroup, YearGroupQuerySet
from .pupil import Pupil, PupilQuerySet
from .teacher import Teacher, TeacherQuerySet
from .classroom import Classroom, ClassroomQuerySet
from .timetable_slot import TimetableSlot, TimetableSlotQuerySet, WeekDay
from .lesson import Lesson, LessonQuerySet

# Type hints
ModelSubclass = Union[
    Profile, School, YearGroup, Pupil, Teacher, Classroom, TimetableSlot, Lesson
]
