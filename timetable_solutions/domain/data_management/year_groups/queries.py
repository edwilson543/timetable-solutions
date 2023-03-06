"""Queries related to managing year group data."""

# Django imports
from django.db import models as django_models

# Local application imports
from data import models


def get_next_year_group_id_for_school(school_id: int) -> int:
    """Get the lowest, unused teacher id for a given school."""
    if year_groups := models.YearGroup.objects.filter(school_id=school_id):
        return (
            year_groups.aggregate(django_models.Max("year_group_id"))[
                "year_group_id__max"
            ]
            + 1
        )
    return 1
