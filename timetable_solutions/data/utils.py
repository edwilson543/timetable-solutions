"""Utility functions / classes / typehints relating to data models"""

# Standard library imports
from typing import TypeVar

# Django imports
from django.db.models import Model

# Local application imports
from .models.timetable_slot import TimetableSlot


# TYPE HINTS
ModelSubclass = TypeVar("ModelSubclass", bound=Model)  # Typehint when referring to specific django Model subclasses


# QUERY METHODS
def get_lessons_per_week(obj: ModelSubclass) -> int:
    """
    Function to get the number of lessons associated with obj per week.
    :param obj - Pupil, Teacher or Classroom instance.
    """
    return sum(lesson.total_required_slots for lesson in obj.lessons.all())


def get_occupied_percentage(obj: ModelSubclass) -> float:
    """
    Function to get the percentage of time obj is occupied per week (including any lunch slots).
    :param obj - Pupil, Teacher or Classroom instance.
    """
    school_id = obj.school.school_access_key
    all_slots = TimetableSlot.objects.get_all_instances_for_school(school_id=school_id)
    utilisation_percentage = obj.get_lessons_per_week() / all_slots.count()
    return utilisation_percentage
