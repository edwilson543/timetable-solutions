"""
Queries related to managing pupil data.
"""

# Django imports
from django.db import models as django_models

# Local application imports
from data import models


def get_pupils(
    *,
    school_id: int,
    search_term: str | None = None,
    year_group: models.YearGroup | None = None,
) -> models.PupilQuerySet:
    """
    Get the pupils matching some search criteria.
    """
    query = django_models.Q(school_id=school_id)
    if search_term:
        try:
            pupil_id = int(search_term)
            query &= django_models.Q(pupil_id=pupil_id)
        except ValueError:
            query &= django_models.Q(
                firstname__icontains=search_term
            ) | django_models.Q(surname__icontains=search_term)
    if year_group:
        query &= django_models.Q(year_group=year_group)
    return models.Pupil.objects.filter(query)


def get_next_pupil_id_for_school(school_id: int) -> int:
    """
    Get the lowest, unused pupil id for a given school.
    """
    if pupils := models.Pupil.objects.filter(school_id=school_id):
        return pupils.aggregate(django_models.Max("pupil_id"))["pupil_id__max"] + 1
    return 1
