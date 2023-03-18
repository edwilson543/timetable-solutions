"""
Tests for filters on the TimetableSlot model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import models
from domain.solver.filters import clashes
from tests import data_factories as data_factories


@pytest.mark.django_db
class TestFilterQuerysetForClashesTimetableSlot:
    @pytest.mark.parametrize("starts_at", [dt.time(hour=9), dt.time(hour=10)])
    def test_filter_for_clashes_no_clashes_expected(self, starts_at: dt.time):
        # Make a slot
        check_slot = data_factories.TimetableSlot(
            starts_at=starts_at,
            ends_at=dt.time(hour=(starts_at.hour + 1), minute=starts_at.minute),
        )
        # And another slot that we do not expect to clash
        data_factories.TimetableSlot(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=check_slot.day_of_week,
        )
        all_slots = models.TimetableSlot.objects.all()

        # Check for clashes at the check time
        check_time = clashes.TimeOfWeek.from_slot(check_slot)
        clashing_slots = clashes.filter_queryset_for_clashes(
            queryset=all_slots, time_of_week=check_time
        )

        # Check the only clash is the check_slot with itself
        assert clashing_slots.get() == check_slot

    @pytest.mark.parametrize(
        "slot_starts_at,check_interval_starts_at",
        [
            (dt.time(hour=9), dt.time(hour=9)),
            (dt.time(hour=8, minute=30), dt.time(hour=9)),
            (dt.time(hour=9), dt.time(hour=8, minute=30)),
        ],
    )
    def test_filter_for_clashes_gives_clash(
        self, slot_starts_at: dt.time, check_interval_starts_at: dt.time
    ):
        slot = data_factories.TimetableSlot(
            starts_at=slot_starts_at,
            ends_at=dt.time(
                hour=(slot_starts_at.hour + 1), minute=slot_starts_at.minute
            ),
        )
        clash_slot = data_factories.TimetableSlot(
            school=slot.school,
            starts_at=slot_starts_at,
            ends_at=dt.time(
                hour=(slot_starts_at.hour + 1), minute=slot_starts_at.minute
            ),
            day_of_week=slot.day_of_week,
        )

        check_time = clashes.TimeOfWeek.from_slot(slot)
        all_slots = models.TimetableSlot.objects.all()

        # Get clashes
        clashing_slots = clashes.filter_queryset_for_clashes(
            queryset=all_slots, time_of_week=check_time
        )

        # Check that the slots clash
        assert clashing_slots.count() == 2
        assert slot in clashing_slots
        assert clash_slot in clashing_slots


@pytest.mark.django_db
class TestFilterQuerysetForClashesBreak:
    """
    Tests for filter_queryset_for_clashes on a Break queryset.
    """

    @pytest.mark.parametrize("starts_at", [dt.time(hour=9), dt.time(hour=10)])
    def test_filter_for_clashes_break_no_clashes_expected(self, starts_at: dt.time):
        # Make a break
        break_ = data_factories.Break(
            starts_at=starts_at,
            ends_at=dt.time(hour=(starts_at.hour + 1), minute=starts_at.minute),
        )

        # Make another break that we do not expect to clash with the first one
        data_factories.Break(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=break_.day_of_week,
        )

        all_breaks = models.Break.objects.all()

        # Check for clashes
        check_time = clashes.TimeOfWeek.from_break(break_)
        break_clashes = clashes.filter_queryset_for_clashes(
            queryset=all_breaks, time_of_week=check_time
        )

        assert break_clashes.get() == break_

    @pytest.mark.parametrize(
        "break_starts_at,slot_starts_at",
        [
            (dt.time(hour=9), dt.time(hour=9)),
            (dt.time(hour=8, minute=30), dt.time(hour=9)),
            (dt.time(hour=9), dt.time(hour=8, minute=30)),
        ],
    )
    def test_filter_for_clashes_gives_clash(self, break_starts_at, slot_starts_at):
        # The break and check interval are both 1 hour long, defined according to parameters
        break_ = data_factories.Break(
            starts_at=break_starts_at,
            ends_at=dt.time(
                hour=(break_starts_at.hour + 1), minute=break_starts_at.minute
            ),
        )
        all_breaks = models.Break.objects.all()

        check_time = clashes.TimeOfWeek(
            starts_at=slot_starts_at,
            ends_at=dt.time(
                hour=(slot_starts_at.hour + 1), minute=slot_starts_at.minute
            ),
            day_of_week=break_.day_of_week,
        )

        # Get clashes and check break in them
        clashing_breaks = clashes.filter_queryset_for_clashes(
            queryset=all_breaks, time_of_week=check_time
        )

        assert clashing_breaks.get() == break_
