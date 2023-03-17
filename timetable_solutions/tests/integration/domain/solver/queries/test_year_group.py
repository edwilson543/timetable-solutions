"""
Tests for solver-related queries of the YearGroup model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from domain.solver.queries import year_group as year_group_solver_queries
from tests import data_factories


@pytest.mark.django_db
class TestCheckIfYearGroupHasClashAtTime:
    def test_busy_when_year_group_already_has_slot_at_time(
        self,
    ):
        # Make a year group with some slot
        yg = data_factories.YearGroup()
        slot = data_factories.TimetableSlot(
            school=yg.school, relevant_year_groups=(yg,)
        )

        # Check if busy
        clash = year_group_solver_queries.check_if_year_group_has_clash_at_time(
            year_group=yg,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        # Check year_group successfully made busy
        assert clash.slots.get() == slot

    def test_busy_when_year_group_already_has_break_at_time(
        self,
    ):
        # Make a year group with some break
        yg = data_factories.YearGroup()

        break_ = data_factories.Break(
            school=yg.school,
            relevant_year_groups=(yg,),
        )

        # Check if busy
        clash = year_group_solver_queries.check_if_year_group_has_clash_at_time(
            year_group=yg,
            starts_at=break_.starts_at,
            ends_at=break_.ends_at,
            day_of_week=break_.day_of_week,
        )

        # Check year_group successfully made busy
        assert clash.breaks.get() == break_

    def test_busy_when_has_slot_at_partially_overlapping_timeslot(self):
        # Make a year group with some slot
        yg = data_factories.YearGroup()
        busy_slot = data_factories.TimetableSlot(
            school=yg.school,
            relevant_year_groups=(yg,),
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )

        # Check if busy
        clash = year_group_solver_queries.check_if_year_group_has_clash_at_time(
            year_group=yg,
            starts_at=dt.time(hour=9, minute=30),
            ends_at=dt.time(hour=10, minute=30),
            day_of_week=busy_slot.day_of_week,
        )

        # Check year_group successfully made busy
        assert clash.slots.get() == busy_slot

    def test_not_busy_when_has_no_slots_or_breaks(self):
        # Make a year group and some slot, but do not assign the slot to the year group
        yg = data_factories.YearGroup()
        slot = data_factories.TimetableSlot(school=yg.school)

        # Check if busy
        clash = year_group_solver_queries.check_if_year_group_has_clash_at_time(
            year_group=yg,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        # Check year_group successfully made busy
        assert not clash
