"""
Operations on the TimetableSlot model affecting db state.
"""

# Standard library imports
import datetime as dt

# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Local application imports
from data import constants, models
from domain.data_management import base_exceptions
from domain.data_management.timetable_slot import queries


class UnableToCreateTimetableSlot(base_exceptions.UnableToCreateModelInstance):
    pass


class UnableToUpdateTimetableSlotTimings(base_exceptions.UnableToUpdateModelInstance):
    pass


class UnableToUpdateTimetableSlotYearGroups(
    base_exceptions.UnableToUpdateModelInstance
):
    pass


def create_new_timetable_slot(
    *,
    school_id: int,
    slot_id: int | None,
    day_of_week: constants.Day,
    starts_at: dt.time,
    ends_at: dt.time,
    relevant_year_groups: models.YearGroupQuerySet | None = None,
) -> models.TimetableSlot:
    """
    Create a new timetable slot in the db.

    :raises UnableToCreateTimetableSlot: if the parameters could not be used to create a slot.
    """
    if not slot_id:
        slot_id = queries.get_next_slot_id_for_school(school_id=school_id)

    try:
        slot = models.TimetableSlot.create_new(
            school_id=school_id,
            slot_id=slot_id,
            day_of_week=day_of_week,
            starts_at=starts_at,
            ends_at=ends_at,
            relevant_year_groups=relevant_year_groups,
        )
    except (IntegrityError, ValidationError) as exc:
        raise UnableToCreateTimetableSlot(
            human_error_message="Could not create timetable slot with the given data."
        ) from exc

    return slot


def update_timetable_slot_timings(
    slot: models.TimetableSlot,
    *,
    day_of_week: constants.Day | None = None,
    starts_at: dt.time | None = None,
    ends_at: dt.time | None = None,
) -> models.TimetableSlot:
    """
    Update a timetable slot timings in the db.

    :raises UnableToUpdateTimetableSlotTimings: if the slot could not be created.
    """
    try:
        return slot.update_slot_timings(
            day_of_week=day_of_week,
            starts_at=starts_at,
            ends_at=ends_at,
        )
    except IntegrityError as exc:
        raise UnableToUpdateTimetableSlotTimings(
            human_error_message="Could not update timetable slot to the given times."
        ) from exc


def update_timetable_slot_year_groups(
    slot: models.TimetableSlot,
    *,
    relevant_year_groups: models.YearGroupQuerySet,
) -> models.TimetableSlot:
    """
    Update the year groups relevant to a timetable slot.

    :raises UnableToUpdateTimetableSlotYearGroups: if the slot could not be created.
    """
    try:
        return slot.update_relevant_year_groups(relevant_year_groups)
    except Exception as exc:
        raise UnableToUpdateTimetableSlotTimings(
            human_error_message="Could not update this timetable slot's year groups."
        ) from exc
