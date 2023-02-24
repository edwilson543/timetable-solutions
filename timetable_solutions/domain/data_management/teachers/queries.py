"""Queries of the teacher model related to user-driven data management."""

from django.db import models as django_models

from data import models


def get_teachers_by_search_term(
    *,
    school_id: int,
    search_term: str,
    n_term_splits: int = 2,
) -> models.TeacherQuerySet:
    """
    Get teachers at a school with id, firstname or surname matching the search term.

    :param school_id: Primary key of the school we are searching for teachers from.
    :param search_term: User input for the search.
    :param n_term_splits: Number of pieces to split the search term into, to loosen
    the match criteria, if we initially get no search results.
    """
    try:
        teacher_id = int(search_term)
        teachers = models.Teacher.objects.filter(
            django_models.Q(school_id=school_id)
            & django_models.Q(teacher_id=teacher_id)
        )
    except ValueError:
        search_term = search_term.lower()
        teachers = models.Teacher.objects.filter(
            django_models.Q(school_id=school_id)
            & (
                django_models.Q(firstname__icontains=search_term)
                | django_models.Q(surname__icontains=search_term)
            )
        )

        # Try a slightly looser query by splitting up the search term
        if teachers.count() == 0:
            search_terms = _get_split_search_terms(
                search_term=search_term, n_term_splits=n_term_splits
            )
            query = django_models.Q()
            for term in search_terms:
                query |= django_models.Q(firstname__icontains=term) | django_models.Q(
                    surname__icontains=term
                )
            teachers = teachers | models.Teacher.objects.filter(
                django_models.Q(school_id=school_id) & query
            )

    return teachers.order_by("teacher_id")


def get_teacher_for_school(school_id: int, teacher_id: int) -> models.Teacher | None:
    """Get the teacher with the teacher id, at the given school."""
    try:
        return models.Teacher.objects.get(teacher_id=teacher_id, school_id=school_id)
    except models.Teacher.DoesNotExist:
        return None


def get_next_teacher_id_for_school(school_id: int) -> int:
    """Get the lowest, unused teacher id for a given school."""
    if teachers := models.Teacher.objects.filter(school_id=school_id):
        return (
            teachers.aggregate(django_models.Max("teacher_id"))["teacher_id__max"] + 1
        )
    return 1


def _get_split_search_terms(search_term: str, n_term_splits: int) -> list[str]:
    """Split up a search term into components to potentially provide more matches."""
    if " " in search_term:
        return search_term.split(" ")

    n_term_splits = min(n_term_splits, len(search_term))
    step = len(search_term) // n_term_splits
    search_terms = [search_term[n : n + step] for n in range(0, len(search_term), step)]
    search_terms = [term for term in search_terms if len(term) > 1]

    return search_terms
