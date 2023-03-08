"""Queries related to managing pupil data."""

# Django imports
from django.db import models as django_models

# Local application imports
from data import models


def get_next_pupil_id_for_school(school_id: int) -> int:
    """Get the lowest, unused pupil id for a given school."""
    if pupils := models.Pupil.objects.filter(school_id=school_id):
        return pupils.aggregate(django_models.Max("pupil_id"))["pupil_id__max"] + 1
    return 1
