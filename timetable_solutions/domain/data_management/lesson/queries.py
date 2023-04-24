"""
Queries related to managing lesson data.
"""

# Django imports
from django.db import models as django_models

# Local application imports
from data import models


def get_lessons(
    *,
    school_id: int,
    search_term: str,
) -> django_models.QuerySet[models.Lesson]:
    """
    Get a filtered subset of lessons, based on id or subject name.
    """
    query = django_models.Q(school_id=school_id)
    query &= django_models.Q(lesson_id=search_term) | django_models.Q(
        subject_name__icontains=search_term
    )

    return models.Lesson.objects.filter(query)
