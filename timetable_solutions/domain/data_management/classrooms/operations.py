"""Operations on the Classroom model affecting db state."""


# Django imports
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import models
from domain.data_management import base_exceptions
from domain.data_management.classrooms import queries


class UnableToCreateClassroom(base_exceptions.UnableToCreateModelInstance):
    pass


class UnableToUpdateClassroom(base_exceptions.UnableToUpdateModelInstance):
    pass


class UnableToDeleteClassroom(base_exceptions.UnableToDeleteModelInstance):
    pass


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
    except IntegrityError as exc:
        raise UnableToCreateClassroom(
            human_error_message=f"Classroom with this data already exists."
        ) from exc


def update_classroom(
    classroom: models.Classroom,
    *,
    building: str | None = None,
    room_number: int | None = None,
) -> models.Classroom:
    """
    Update a classroom in the db.

    raises CouldNotUpdateClassroom if it wasn't possible.
    """
    try:
        return classroom.update(building=building, room_number=room_number)
    except Exception as exc:
        raise UnableToUpdateClassroom(
            human_error_message="Unable to update details for this classroom"
        ) from exc


def delete_classroom(
    classroom: models.Classroom,
) -> models.Classroom:
    """
    Delete a classroom from the db.

    raises CouldNotDeleteClassroom if it wasn't possible.
    """
    try:
        return classroom.delete()
    except ProtectedError as exc:
        protected_relations = {
            model.Constant.human_string_singular for model in exc.protected_objects
        }
        protected_str = ", ".join(protected_relations)
        raise UnableToDeleteClassroom(
            human_error_message=f"Unable to delete classroom - at least one {protected_str} still use this classroom!"
        ) from exc
