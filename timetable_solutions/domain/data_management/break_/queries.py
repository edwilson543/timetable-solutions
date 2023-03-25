"""
Queries related to managing break data.
"""

# Django imports
from django.db import models as django_models

# Local application imports
from data import constants, models


def get_breaks(
    *,
    school_id: int,
    search_term: str | None = None,
    day: constants.Day | None = None,
    year_group: models.YearGroup | None = None,
) -> models.BreakQuerySet:
    """
    Get the breaks matching the parameters.
    """
    query = django_models.Q(school_id=school_id)
    if search_term:
        query &= django_models.Q(break_id__icontains=search_term) | django_models.Q(
            break_name__icontains=search_term
        )
    if day:
        query &= django_models.Q(day_of_week=day)
    if year_group:
        query &= django_models.Q(relevant_year_groups=year_group)
    return models.Break.objects.filter(query)
