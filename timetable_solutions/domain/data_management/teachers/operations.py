"""Operations on the Teacher model affecting db state."""

from django.db import IntegrityError

from . import exceptions
from data import models


def create_new_teacher(
    *, school_id: int, teacher_id: int, firstname: str, surname: str, title: str
) -> models.Teacher:
    """
    Create a new teacher in the db and handle any exceptions.

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
    except IntegrityError:
        raise exceptions.CouldNotCreateTeacher
