"""Operations on the Teacher model affecting db state."""

# Local application imports
from data import models

from . import exceptions, queries


def create_new_teacher(
    *, school_id: int, teacher_id: int | None, firstname: str, surname: str, title: str
) -> models.Teacher:
    """
    Create a new teacher in the db.

    :raises CouldNotCreateTeacher: if the parameters could not be used to create a teacher.
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
    except Exception:
        raise exceptions.CouldNotCreateTeacher


def update_teacher(
    *,
    teacher: models.Teacher,
    firstname: str | None = None,
    surname: str | None,
    title: str | None = None
) -> models.Teacher:
    """
    Update a teacher in the db.

    raises CouldNotUpdateTeacher if it wasn't possible.
    """
    try:
        return teacher.update(firstname=firstname, surname=surname, title=title)
    except Exception:
        raise exceptions.CouldNotUpdateTeacher


def delete_teacher(teacher: models.Teacher) -> tuple[int, dict[str, int]]:
    """
    Delete a teacher in the db.

    :return: Tuple of the number of objects deleted, and a dict mapping the model to number of instances
    of that model that were deleted.
    :raises CouldNotDeleteTeacher: If the teacher couldn't be deleted (e.g due to a protected foreign key)
    """
    try:
        return teacher.delete()
    except Exception:
        raise exceptions.CouldNotDeleteTeacher
