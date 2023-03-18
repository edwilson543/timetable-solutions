"""
Queries related to managing timetable slot data.
"""

# Django imports
from django.db import models as django_models

# Local application imports
from data import constants, models


def get_timetable_slots(
    *,
    school_id: int,
    slot_id: int | None = None,
    day: constants.Day | None = None,
    year_group: models.YearGroup | None = None,
) -> models.TimetableSlotQuerySet:
    """
    Get the timetable slots matching the parameters.
    """
    query = django_models.Q(school_id=school_id)
    if slot_id:
        query &= django_models.Q(slot_id=slot_id)
    if day:
        query &= django_models.Q(day_of_week=day)
    if year_group:
        query &= django_models.Q(relevant_year_groups=year_group)
    return models.TimetableSlot.objects.filter(query)


def get_next_slot_id_for_school(school_id: int) -> int:
    """
    Get the lowest, unused slot id for a given school.
    """
    if slot := models.TimetableSlot.objects.filter(school_id=school_id):
        return slot.aggregate(django_models.Max("slot_id"))["slot_id__max"] + 1
    return 1
