"""
Operations on the YearGroup model affecting db state.
"""

# Django imports
from django.db import IntegrityError

# Local application imports
from data import models
from domain.data_management import base_exceptions
from domain.data_management.year_groups import queries


class UnableToCreateYearGroup(base_exceptions.UnableToCreateModelInstance):
    pass


class UnableToUpdateYearGroup(base_exceptions.UnableToUpdateModelInstance):
    pass


class UnableToDeleteYearGroup(base_exceptions.UnableToDeleteModelInstance):
    pass


def create_new_year_group(
    *, school_id: int, year_group_id: int | None, year_group_name: str
) -> models.YearGroup:
    """
    Create a new year group in the db.

    :raises UnableToCreateYearGroup: if the parameters could not be used to create a year group.
    """
    if not year_group_id:
        year_group_id = queries.get_next_year_group_id_for_school(school_id=school_id)
    try:
        return models.YearGroup.create_new(
            school_id=school_id,
            year_group_id=year_group_id,
            year_group_name=year_group_name,
        )
    except IntegrityError as exc:
        raise UnableToCreateYearGroup(
            human_error_message="Year group with this data already exists!"
        ) from exc


def update_year_group(
    year_group: models.YearGroup,
    *,
    year_group_name: str | None = None,
) -> models.YearGroup:
    """
    Update a year group in the db.

    raises UnableToUpdateYearGroup if it wasn't possible.
    """
    try:
        return year_group.update(year_group_name=year_group_name)
    except Exception as exc:
        raise UnableToUpdateYearGroup(
            human_error_message="Unable to update details for this year group."
        ) from exc


def delete_year_group(year_group: models.YearGroup) -> tuple[int, dict[str, int]]:
    """
    Delete a year group in the db.

    :return: Tuple of the number of objects deleted, and a dict mapping the model to number of instances
    of that model that were deleted.
    :raises UnableToDeleteYearGroup: If the year group couldn't be deleted
    """
    try:
        return year_group.delete()
    except Exception as exc:
        raise UnableToDeleteYearGroup(
            human_error_message="Unable to delete this year group."
        ) from exc
