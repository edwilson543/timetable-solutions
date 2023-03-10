"""Operations on the Break model affecting db state."""
# Standard library imports
import datetime as dt

# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Local application imports
from data import constants, models

from . import exceptions


def create_new_break(
    *,
    school_id: int,
    break_id: str,
    break_name: str,
    day_of_week: constants.Day,
    starts_at: dt.time,
    ends_at: dt.time,
    teachers: models.TeacherQuerySet,
    relevant_year_groups: models.YearGroupQuerySet,
) -> models.Break:
    """
    Create a new break in the db.

    :raises CouldNotCreateBreak: if the parameters could not be used to create a break.
    """
    try:
        return models.Break.create_new(
            school_id=school_id,
            break_id=break_id,
            break_name=break_name,
            starts_at=starts_at,
            ends_at=ends_at,
            day_of_week=day_of_week,
            teachers=teachers,
            relevant_year_groups=relevant_year_groups,
        )
    except (IntegrityError, ValidationError, ValueError) as exc:
        raise exceptions.CouldNotCreateBreak from exc
