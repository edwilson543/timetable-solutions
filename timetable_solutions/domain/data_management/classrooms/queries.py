"""Queries of the classroom model related to user-driven data management."""


# Django imports
from django.db import models as django_models

# Local application imports
from data import models


def get_next_classroom_id_for_school(school_id: int) -> int:
    """Get the lowest, unused classroom id for a given school."""
    if classrooms := models.Classroom.objects.filter(school_id=school_id):
        return (
            classrooms.aggregate(django_models.Max("classroom_id"))["classroom_id__max"]
            + 1
        )
    return 1
