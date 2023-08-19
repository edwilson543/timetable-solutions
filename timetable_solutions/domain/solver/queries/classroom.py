"""
Solver-related queries of the classroom model.
"""

# Standard library imports
import datetime as dt

# Local application imports
from data import constants, models
from domain.solver.filters import clashes


def check_if_classroom_occupied_at_time(
    classroom: models.Classroom,
    *,
    starts_at: dt.time,
    ends_at: dt.time,
    day_of_week: constants.Day,
) -> models.TimetableSlotQuerySet | None:
    """
    Get the slots a classroom is occupied with at a given time, if any.
    """
    time_of_week = clashes.TimeOfWeek(
        starts_at=starts_at, ends_at=ends_at, day_of_week=day_of_week
    )
    user_defined_slots = models.TimetableSlot.objects.filter(
        user_lessons__classroom=classroom
    )
    lesson_clashes = clashes.filter_queryset_for_clashes(
        queryset=user_defined_slots, time_of_week=time_of_week
    )

    n_commitments = lesson_clashes.count()

    if n_commitments == 0:
        return None

    return lesson_clashes
