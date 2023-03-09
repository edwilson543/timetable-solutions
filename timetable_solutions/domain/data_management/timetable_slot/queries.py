"""Queries related to managing timetable slot data."""

# Django imports
from django.db import models as django_models

# Local application imports
from data import models


def get_next_slot_id_for_school(school_id: int) -> int:
    """Get the lowest, unused slot id for a given school."""
    if slot := models.TimetableSlot.objects.filter(school_id=school_id):
        return slot.aggregate(django_models.Max("slot_id"))["slot_id__max"] + 1
    return 1
