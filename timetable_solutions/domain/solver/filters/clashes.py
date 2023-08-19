"""
Filters for database content that 'clashes' in time.

For example:
 * A pupil / teacher / classroom cannot have lessons that occur at clashing slots
 * A year group cannot have 2 slots that overlap
 * A pupil / teacher / classroom can't be assigned two clashing breaks
"""

# Standard library imports
import dataclasses
import datetime as dt
import typing

# Django imports
from django.db import models as django_models

# Local application imports
from data import constants, models


@dataclasses.dataclass
class Clash:
    """
    Record the slots and breaks that clashed with some time.
    """

    slots: models.TimetableSlotQuerySet
    breaks: models.BreakQuerySet


@dataclasses.dataclass
class TimeOfWeek:
    """
    Bundle up the time of week that a slot or break spans.
    """

    starts_at: dt.time
    ends_at: dt.time
    day_of_week: constants.Day

    @classmethod
    def from_slot(cls, slot: models.TimetableSlot) -> "TimeOfWeek":
        return cls(
            starts_at=slot.starts_at, ends_at=slot.ends_at, day_of_week=slot.day_of_week
        )

    @classmethod
    def from_break(cls, break_: models.Break) -> "TimeOfWeek":
        return cls(
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
        )


@typing.overload
def filter_queryset_for_clashes(
    queryset: models.TimetableSlotQuerySet, *, time_of_week: TimeOfWeek
) -> models.TimetableSlotQuerySet:
    """
    Return a TimetableSlotQuerySet if filtering a TimetableSlotQuerySet.
    """
    ...


@typing.overload
def filter_queryset_for_clashes(
    queryset: models.BreakQuerySet, *, time_of_week: TimeOfWeek
) -> models.BreakQuerySet:
    """
    Return a BreakQueryset if filtering a BreakQueryset.
    """
    ...


def filter_queryset_for_clashes(
    queryset: models.TimetableSlotQuerySet | models.BreakQuerySet,
    *,
    time_of_week: TimeOfWeek
) -> models.TimetableSlotQuerySet | models.BreakQuerySet:
    """
    Filter a queryset of slots or breaks against a time of the week.
    :return The items in the queryset that clash with the passed time, non-inclusively.

    The use case for this is to check whether teachers / classrooms / pupil / year groups
    are already busy at any point during a give time of the week.
    """
    return queryset.filter(
        (
            (
                # Items of the queryset time_of_week.starts_at falls within
                django_models.Q(starts_at__lt=time_of_week.starts_at)
                & django_models.Q(ends_at__gt=time_of_week.starts_at)
            )
            | (
                # Items of the queryset time_of_week.ends_at falls within
                django_models.Q(starts_at__lt=time_of_week.ends_at)
                & django_models.Q(ends_at__gt=time_of_week.ends_at)
            )
            | (
                # EXACT MATCH - we want slots to clash with other slots starting and finishing
                # at the same time
                django_models.Q(starts_at=time_of_week.starts_at)
                | django_models.Q(ends_at=time_of_week.ends_at)
            )
        )
        & django_models.Q(day_of_week=time_of_week.day_of_week)
    ).distinct()
