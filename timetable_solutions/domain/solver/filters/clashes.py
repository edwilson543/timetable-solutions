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

    @property
    def open_interval(self) -> tuple[dt.time, dt.time]:
        """
        Create a 'fake' open interval covered by a timespan.

        This is so that comparing two intervals doesn't give undesired clashes when using
        the django queryset look __range, which is inclusive.
        """
        one_second = dt.timedelta(seconds=1)

        open_start_time = (
            dt.datetime.combine(date=dt.datetime.min, time=self.starts_at) + one_second
        ).time()

        open_end_time = (
            dt.datetime.combine(date=dt.datetime.min, time=self.ends_at) - one_second
        ).time()

        return open_start_time, open_end_time


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
    clash_range = time_of_week.open_interval
    # Note the django __range filter is inclusive, hence the open interval is essential,
    # otherwise we just get slots that start/finish at the same time e.g. 9-10, 10-11...

    return queryset.filter(
        (
            (
                # OVERLAPPING clashes
                django_models.Q(starts_at__range=clash_range)
                | django_models.Q(ends_at__range=clash_range)
            )
            | (
                # EXACT MATCH clashes
                # We do however want slots to clash with themselves / other slots starting and finishing
                # at the same time, since a user may have defined slots covering the same time span
                django_models.Q(starts_at=time_of_week.starts_at)
                | django_models.Q(ends_at=time_of_week.ends_at)
            )
        )
        & django_models.Q(day_of_week=time_of_week.day_of_week)
    )
