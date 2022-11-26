"""
Convenience imports of all models.
Note that we also import the custom model managers to use as type hints when a function returns a queryset specifically
from that model.
"""
from .user_profile import Profile, UserRole
from .school import School
from .pupil import Pupil, PupilQuerySet
from .teacher import Teacher, TeacherQuerySet
from .classroom import Classroom
from .timetable_slot import TimetableSlot, TimetableSlotQuerySet, WeekDay
from .lesson import Lesson, LessonQuerySet
