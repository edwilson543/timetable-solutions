"""
Solver-related queries of the pupil model.
"""

# Standard library imports
import datetime as dt

# Local application imports
from data import constants, models
from domain.solver.filters import clashes


def check_if_pupil_busy_at_time(
    pupil: models.Pupil,
    *,
    starts_at: dt.time,
    ends_at: dt.time,
    day_of_week: constants.Day,
) -> clashes.Clash | None:
    """
    Get the slots and breaks a pupil is busy with at a given time, if any.
    """
    time_of_week = clashes.TimeOfWeek(
        starts_at=starts_at, ends_at=ends_at, day_of_week=day_of_week
    )
    user_defined_slots = models.TimetableSlot.objects.filter(user_lessons__pupils=pupil)
    lesson_clashes = clashes.filter_queryset_for_clashes(
        queryset=user_defined_slots, time_of_week=time_of_week
    )

    breaks = pupil.year_group.breaks.all()
    break_clashes = clashes.filter_queryset_for_clashes(
        queryset=breaks, time_of_week=time_of_week
    )

    n_commitments = lesson_clashes.count() + break_clashes.count()

    if n_commitments == 0:
        return None

    return clashes.Clash(slots=lesson_clashes, breaks=break_clashes)
