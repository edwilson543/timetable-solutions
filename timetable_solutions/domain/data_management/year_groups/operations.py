"""Operations on the YearGroup model affecting db state."""

# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import models

from . import exceptions, queries


def create_new_year_group(
    *, school_id: int, year_group_id: int | None, year_group_name: str
) -> models.YearGroup:
    """
    Create a new year group in the db.

    :raises CouldNotCreateYearGroup: if the parameters could not be used to create a year group.
    """
    if not year_group_id:
        year_group_id = queries.get_next_year_group_id_for_school(school_id=school_id)
    try:
        return models.YearGroup.create_new(
            school_id=school_id,
            year_group_id=year_group_id,
            year_group_name=year_group_name,
        )
    except (IntegrityError, ValidationError, ValueError) as exc:
        raise exceptions.CouldNotCreateYearGroup from exc


def update_year_group(
    *,
    year_group: models.YearGroup,
    year_group_name: str | None = None,
) -> models.YearGroup:
    """
    Update a year group in the db.

    raises CouldNotUpdateYearGroup if it wasn't possible.
    """
    try:
        return year_group.update(year_group_name=year_group_name)
    except (ValidationError, ValueError) as exc:
        raise exceptions.CouldNotUpdateYearGroup from exc


def delete_year_group(year_group: models.YearGroup) -> tuple[int, dict[str, int]]:
    """
    Delete a year group in the db.

    :return: Tuple of the number of objects deleted, and a dict mapping the model to number of instances
    of that model that were deleted.
    :raises CouldNotDeleteYearGroup: If the year group couldn't be deleted (e.g due to a protected foreign key)
    """
    try:
        return year_group.delete()
    except ProtectedError as exc:
        raise exceptions.CouldNotDeleteYearGroup from exc
