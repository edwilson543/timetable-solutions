"""Operations on the Pupil model affecting db state."""

# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Local application imports
from data import models
from domain.data_management import base_exceptions

from . import queries


class UnableToCreatePupil(base_exceptions.UnableToCreateModelInstance):
    pass


class UnableToUpdatePupil(base_exceptions.UnableToUpdateModelInstance):
    pass


class UnableToDeletePupil(base_exceptions.UnableToDeleteModelInstance):
    pass


def create_new_pupil(
    *,
    school_id: int,
    pupil_id: int,
    firstname: str,
    surname: str,
    year_group_id: int,
) -> models.Pupil:
    """
    Create a new pupil in the db.

    :raises CouldNotCreatePupil: if the parameters could not be used to create a pupil.
    """
    try:
        year_group = models.YearGroup.objects.get_individual_year_group(
            school_id=school_id, year_group_id=year_group_id
        )
    except models.YearGroup.DoesNotExist:
        raise UnableToCreatePupil(
            human_error_message=f"Year group with id {year_group_id} does not exist!"
        )

    if not pupil_id:
        pupil_id = queries.get_next_pupil_id_for_school(school_id=school_id)

    try:
        return models.Pupil.create_new(
            school_id=school_id,
            pupil_id=pupil_id,
            firstname=firstname,
            surname=surname,
            year_group=year_group,
        )
    except (IntegrityError, ValidationError) as exc:
        raise UnableToCreatePupil(
            human_error_message="Could not create pupil with the given data."
        ) from exc


def update_pupil(
    pupil: models.Pupil,
    *,
    firstname: str | None = None,
    surname: str | None = None,
    year_group: models.YearGroup | None = None,
) -> models.Pupil:
    """
    Update a pupil in the db.

    raises CouldNotUpdatePupil if it wasn't possible.
    """
    try:
        return pupil.update(firstname=firstname, surname=surname, year_group=year_group)
    except Exception:
        raise UnableToUpdatePupil(
            human_error_message="Unable to update details for this pupil."
        )
