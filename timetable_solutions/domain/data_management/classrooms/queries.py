"""
Queries of the classroom model related to user-driven data management.
"""


# Django imports
from django.db import models as django_models

# Local application imports
from data import models


def get_classrooms(
    *,
    school_id: int,
    classroom_id: int | None = None,
    building: str | None = None,
    room_number: int | None = None,
) -> django_models.QuerySet[models.Classroom]:
    """
    Get classrooms at a school matching the parameters.
    """
    query = django_models.Q(school_id=school_id)
    if classroom_id:
        query &= django_models.Q(classroom_id=classroom_id)
    if building:
        query &= django_models.Q(building__iexact=building)
    if room_number:
        query &= django_models.Q(room_number=room_number)
    return models.Classroom.objects.filter(query)


def get_next_classroom_id_for_school(school_id: int) -> int:
    """Get the lowest, unused classroom id for a given school."""
    if classrooms := models.Classroom.objects.filter(school_id=school_id):
        return (
            classrooms.aggregate(django_models.Max("classroom_id"))["classroom_id__max"]
            + 1
        )
    return 1
