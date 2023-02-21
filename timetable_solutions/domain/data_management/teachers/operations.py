"""Operations on the Teacher model affecting db state."""

from django.db import IntegrityError
from django.core import exceptions as django_exceptions

from . import exceptions
from data import models


def create_new_teacher(
    *, school_id: int, teacher_id: int, firstname: str, surname: str, title: str
) -> models.Teacher:
    """
    Create a new teacher in the db.

    :raises CouldNotCreateTeacher: if the parameters could not be used to create a teacher.
    """
    try:
        return models.Teacher.create_new(
            school_id=school_id,
            teacher_id=teacher_id,
            firstname=firstname,
            surname=surname,
            title=title,
        )
    except (IntegrityError, django_exceptions.ValidationError):
        raise exceptions.CouldNotCreateTeacher


def update_teacher(
    *,
    teacher: models.Teacher,
    firstname: str | None = None,
    surname: str | None,
    title: str | None = None
) -> None:
    """
    Update a teacher in the db.

    """
    try:
        teacher.update(firstname=firstname, surname=surname, title=title)
    except django_exceptions.ValidationError:
        raise exceptions.CouldNotCreateTeacher
