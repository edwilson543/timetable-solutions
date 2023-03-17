"""
Solver-related queries of the year group model.
"""

# Standard library imports
import datetime as dt

# Local application imports
from data import constants, models
from domain.solver.filters import clashes


def check_if_year_group_has_clash_at_time(
    year_group: models.YearGroup,
    *,
    starts_at: dt.time,
    ends_at: dt.time,
    day_of_week: constants.Day,
) -> clashes.Clash | None:
    """
    Get the slots and breaks a year group already has assigned at a given time, if any.

    This is to prevent users from creating two overlapping timeslots / breaks or an
    overlapping timeslot and break for the same year group.
    """
    time_of_week = clashes.TimeOfWeek(
        starts_at=starts_at, ends_at=ends_at, day_of_week=day_of_week
    )
    existing_slots = year_group.slots.all()
    slot_clashes = clashes.filter_queryset_for_clashes(
        queryset=existing_slots, time_of_week=time_of_week
    )

    existing_breaks = year_group.breaks.all()
    break_clashes = clashes.filter_queryset_for_clashes(
        queryset=existing_breaks, time_of_week=time_of_week
    )

    n_commitments = slot_clashes.count() + break_clashes.count()

    if n_commitments == 1:
        return clashes.Clash(slots=slot_clashes, breaks=break_clashes)
    elif n_commitments == 0:
        return None
    else:
        raise ValueError(
            f"Year group with pk {year_group.pk} has ended up with more than 1 slot "
            f"or break at {starts_at} - {ends_at} on {day_of_week.value}"
        )
