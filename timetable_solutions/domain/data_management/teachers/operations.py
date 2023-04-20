"""Operations on the Teacher model affecting db state."""

# Django imports
from django.db import IntegrityError
from django.db.models import ProtectedError

# Local application imports
from data import models
from domain import base_exceptions
from domain.data_management.teachers import queries


class UnableToCreateTeacher(base_exceptions.UnableToCreateModelInstance):
    pass


class UnableToUpdateTeacher(base_exceptions.UnableToUpdateModelInstance):
    pass


class UnableToDeleteTeacher(base_exceptions.UnableToDeleteModelInstance):
    pass


def create_new_teacher(
    *, school_id: int, teacher_id: int | None, firstname: str, surname: str, title: str
) -> models.Teacher:
    """
    Create a new teacher in the db.

    :raises UnableToCreateTeacher: if the parameters could not be used to create a teacher.
    """
    if not teacher_id:
        teacher_id = queries.get_next_teacher_id_for_school(school_id=school_id)
    try:
        return models.Teacher.create_new(
            school_id=school_id,
            teacher_id=teacher_id,
            firstname=firstname,
            surname=surname,
            title=title,
        )
    except IntegrityError as exc:
        raise UnableToCreateTeacher(
            human_error_message=f"Teacher with id {teacher_id} already exists!"
        ) from exc


def update_teacher(
    teacher: models.Teacher,
    *,
    firstname: str | None = None,
    surname: str | None,
    title: str | None = None,
) -> models.Teacher:
    """
    Update a teacher in the db.

    raises UnableToUpdateTeacher if it wasn't possible.
    """
    try:
        return teacher.update(firstname=firstname, surname=surname, title=title)
    except Exception as exc:
        raise UnableToUpdateTeacher(
            human_error_message="Unable to update details for this teacher."
        ) from exc


def delete_teacher(teacher: models.Teacher) -> tuple[int, dict[str, int]]:
    """
    Delete a teacher in the db.

    :return: Tuple of the number of objects deleted, and a dict mapping the model to number of instances
    of that model that were deleted.
    :raises UnableToDeleteTeacher: If the teacher couldn't be deleted (e.g due to a protected foreign key)
    """
    try:
        return teacher.delete()
    except ProtectedError as exc:
        protected_relations = {
            model.Constant.human_string_singular for model in exc.protected_objects
        }
        protected_str = ", ".join(protected_relations)
        raise UnableToDeleteTeacher(
            human_error_message=f"Unable to delete teacher - at least one {protected_str} still references this teacher!"
        ) from exc
