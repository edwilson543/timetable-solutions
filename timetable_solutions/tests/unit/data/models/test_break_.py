# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Local application imports
from data import constants, models
from tests import data_factories


@pytest.mark.django_db
class TestBreakQuerySet:
    """
    Unit tests for the Break manager.
    """

    @pytest.mark.parametrize(
        "break_starts_at,slot_starts_at",
        [
            (dt.time(hour=9), dt.time(hour=9)),
            (dt.time(hour=8, minute=30), dt.time(hour=9)),
            (dt.time(hour=9), dt.time(hour=8, minute=30)),
        ],
    )
    def test_filter_for_clashes_gives_clash(self, break_starts_at, slot_starts_at):
        """Test that a slot and break at the exact same time clash."""
        # The break and slot are both 1 hour long, defined according to parameters
        break_ = data_factories.Break(
            starts_at=break_starts_at,
            ends_at=dt.time(
                hour=(break_starts_at.hour + 1), minute=break_starts_at.minute
            ),
        )
        slot = data_factories.TimetableSlot(
            school=break_.school,
            starts_at=slot_starts_at,
            ends_at=dt.time(
                hour=(slot_starts_at.hour + 1), minute=slot_starts_at.minute
            ),
            day_of_week=break_.day_of_week,
        )

        # Get clashes and check break in them
        clashes = models.Break.objects.filter_for_clashes(slot)

        assert clashes.count() == 1
        assert break_ in clashes

    @pytest.mark.parametrize("starts_at", [dt.time(hour=9), dt.time(hour=10)])
    def test_filter_for_clashes_break_at_different_time_to_slot_gives_no_clashes(
        self, starts_at
    ):
        """Test that a slot and break at different times don't clash."""
        # Make a break and slot at different times
        break_ = data_factories.Break(
            starts_at=starts_at,
            ends_at=dt.time(hour=(starts_at.hour + 1), minute=starts_at.minute),
        )
        slot = data_factories.TimetableSlot(
            school=break_.school,
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
        )

        # Get clashes and check break in them
        clashes = models.Break.objects.filter_for_clashes(slot)

        assert clashes.count() == 0


@pytest.mark.django_db
class TestCreateNewBreak:
    def test_create_new_for_valid_break(self):
        # Get some teachers and year groups to add
        school = data_factories.School()
        teacher = data_factories.Teacher()
        yg = data_factories.YearGroup()

        # Make the break
        break_ = models.Break.create_new(
            school_id=school.school_access_key,
            break_id="1",
            break_name="Morning break",
            starts_at=dt.time(hour=11, minute=30),
            ends_at=dt.time(hour=12),
            day_of_week=constants.Day.MONDAY,
            teachers=teacher,
            relevant_year_groups=yg,
        )

        # Check break in db and defined as expected
        all_breaks = models.Break.objects.all()
        assert all_breaks.count() == 1
        assert break_ in all_breaks

        all_teachers = break_.teachers.all()
        assert all_teachers.count() == 1
        assert teacher in all_teachers

        all_ygs = break_.relevant_year_groups.all()
        assert all_ygs.count() == 1
        assert yg in all_ygs

    def test_create_new_raises_when_break_id_already_taken(self):
        break_ = data_factories.Break()

        # Try to make another break with the same id
        with pytest.raises(IntegrityError):
            models.Break.create_new(
                school_id=break_.school.school_access_key,
                break_id=break_.break_id,
                break_name="test",
                starts_at=dt.time(hour=11, minute=30),
                ends_at=dt.time(hour=12),
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_raises_when_break_ends_before_it_starts(self):
        school = data_factories.School()

        # Try to make another break with the same id
        with pytest.raises(IntegrityError):
            models.Break.create_new(
                school_id=school.school_access_key,
                break_id="morning-break",
                break_name="test",
                starts_at=dt.time(hour=12),
                ends_at=dt.time(hour=11),  # Note ends after starts
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_raises_when_break_ends_when_it_starts(self):
        school = data_factories.School()

        # Try to make another break with the same id
        with pytest.raises(IntegrityError):
            models.Break.create_new(
                school_id=school.school_access_key,
                break_id="morning-break",
                break_name="test",
                starts_at=dt.time(hour=12),
                ends_at=dt.time(hour=12),  # Note ends at same time
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_create_new_raises_for_invalid_day_of_week(self):
        school = data_factories.School()

        # Try to make another break with the same id
        with pytest.raises(ValidationError):
            models.Break.create_new(
                school_id=school.school_access_key,
                break_id="morning-break",
                break_name="test",
                starts_at=dt.time(hour=12),
                ends_at=dt.time(hour=13),
                day_of_week=100,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )


@pytest.mark.django_db
class TestDeleteAllInstancesForSchool:
    def test_delete_all_breaks_for_school_successful(self):
        """
        Test that we can delete all the breaks associated with a school.
        """
        # Make a break
        break_ = data_factories.Break()

        # Try deleting the break
        models.Break.delete_all_breaks_for_school(
            school_id=break_.school.school_access_key
        )

        # Check break was deleted
        assert models.Break.objects.count() == 0
