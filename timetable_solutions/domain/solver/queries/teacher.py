"""
Solver-related queries of the teacher model.
"""

# Standard library imports
import datetime as dt

# Local application imports
from data import constants, models
from domain.solver.filters import clashes


def check_if_teacher_busy_at_time(
    teacher: models.Teacher,
    *,
    starts_at: dt.time,
    ends_at: dt.time,
    day_of_week: constants.Day,
) -> clashes.Clash | None:
    """
    Get the slots and breaks a teacher is busy with at a given time, if any.
    """
    time_of_week = clashes.TimeOfWeek(
        starts_at=starts_at, ends_at=ends_at, day_of_week=day_of_week
    )
    user_defined_slots = models.TimetableSlot.objects.filter(
        user_lessons__teacher=teacher
    )
    lesson_clashes = clashes.filter_queryset_for_clashes(
        queryset=user_defined_slots, time_of_week=time_of_week
    )

    breaks = teacher.breaks.all()
    break_clashes = clashes.filter_queryset_for_clashes(
        queryset=breaks, time_of_week=time_of_week
    )

    n_commitments = lesson_clashes.count() + break_clashes.count()

    if n_commitments == 1:
        return clashes.Clash(slots=lesson_clashes, breaks=break_clashes)
    elif n_commitments == 0:
        return None
    else:
        raise ValueError(
            f"Teacher {teacher}, {teacher.pk} has ended up with more than 1 commitment"
            f" at {starts_at} - {ends_at} on {day_of_week.value}"
        )
