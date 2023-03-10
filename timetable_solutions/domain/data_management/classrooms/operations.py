"""Operations on the Classroom model affecting db state."""


# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Local application imports
from data import models

from . import exceptions, queries


def create_new_classroom(
    *, school_id: int, classroom_id: int | None, building: str, room_number: int
) -> models.Classroom:
    """
    Create a new classroom in the db.

    :raises CouldNotCreateClassroom: if the parameters could not be used to create a classroom.
    """
    if not classroom_id:
        classroom_id = queries.get_next_classroom_id_for_school(school_id=school_id)
    try:
        return models.Classroom.create_new(
            school_id=school_id,
            classroom_id=classroom_id,
            building=building,
            room_number=room_number,
        )
    except (IntegrityError, ValidationError, ValueError) as exc:
        raise exceptions.CouldNotCreateClassroom from exc


def update_classroom(
    classroom: models.Classroom,
    *,
    building: str | None = None,
    room_number: int | None = None
) -> models.Classroom:
    """
    Update a classroom in the db.

    raises CouldNotUpdateClassroom if it wasn't possible.
    """
    try:
        return classroom.update(building=building, room_number=room_number)
    except (ValidationError, ValueError) as exc:
        raise exceptions.CouldNotUpdateClassroom from exc
