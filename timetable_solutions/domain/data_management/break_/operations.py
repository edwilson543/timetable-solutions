"""
Operations on the Break model affecting db state.
"""
# Standard library imports
import datetime as dt

# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Local application imports
from data import constants, models
from domain.data_management import base_exceptions


class UnableToCreateBreak(base_exceptions.UnableToCreateModelInstance):
    pass


class UnableToUpdateBreakTimings(base_exceptions.UnableToUpdateModelInstance):
    pass


class UnableToUpdateBreakYearGroups(base_exceptions.UnableToUpdateModelInstance):
    pass


class UnableToDeleteBreak(base_exceptions.UnableToDeleteModelInstance):
    pass


def create_new_break(
    *,
    school_id: int,
    break_id: str,
    break_name: str,
    day_of_week: constants.Day,
    starts_at: dt.time,
    ends_at: dt.time,
    teachers: models.TeacherQuerySet | None = None,
    relevant_year_groups: models.YearGroupQuerySet | None = None,
    relevant_to_all_teachers: bool = False,
    relevant_to_all_year_groups: bool = False,
) -> models.Break:
    """
    Create a new break in the db.

    :raises UnableToCreateBreak: if the parameters could not be used to create a break.
    """
    if relevant_to_all_teachers:
        teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=school_id
        )

    if relevant_to_all_year_groups:
        relevant_year_groups = models.YearGroup.objects.get_all_instances_for_school(
            school_id=school_id
        )

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
    except IntegrityError as exc:
        raise UnableToCreateBreak(
            human_error_message="A break with the given id already exists!"
        ) from exc
    except ValidationError as exc:
        raise UnableToCreateBreak(
            human_error_message="Could not create break with the given data."
        ) from exc


def update_break_timings(
    break_: models.Break,
    *,
    break_name: str = "",
    day_of_week: constants.Day | None = None,
    starts_at: dt.time | None = None,
    ends_at: dt.time | None = None,
) -> models.Break:
    """
    Update a break in the db.

    :raises UnableToUpdateBreakTimings: if the break could not be updated.
    """
    try:
        return break_.update_break_timings(
            break_name=break_name,
            day_of_week=day_of_week,
            starts_at=starts_at,
            ends_at=ends_at,
        )
    except IntegrityError as exc:
        raise UnableToUpdateBreakTimings(
            human_error_message="Could not update break."
        ) from exc


def update_break_year_groups(
    break_: models.Break,
    *,
    relevant_year_groups: models.YearGroupQuerySet,
) -> models.Break:
    """
    Update the year groups relevant to a break.

    :raises UnableToUpdateBreakYearGroups: if the break could not be updated.
    """
    try:
        return break_.update_relevant_year_groups(relevant_year_groups)
    except Exception as exc:
        raise UnableToUpdateBreakTimings(
            human_error_message="Could not update this break's year groups."
        ) from exc


def delete_break(break_: models.Break) -> tuple[int, dict[str, int]]:
    """
    Delete a break from the db.

    :return: Tuple of the number of objects deleted, and a dict mapping the model to number of instances
    of that model that were deleted.
    :raises UnableToDeleteBreak: If the break couldn't be deleted.
    """
    try:
        return break_.delete()
    except Exception as exc:
        raise UnableToDeleteBreak(
            human_error_message="Unable to delete this break!"
        ) from exc
