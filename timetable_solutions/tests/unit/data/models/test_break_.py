# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.db import IntegrityError

# Local application imports
from data import constants
from data import models
from tests import factories


@pytest.mark.django_db
class TestBreakQuerySet:
    """
    Unit tests for the Break manager.
    """

    @pytest.mark.parametrize(
        "break_starts_at,period_starts_at",
        [
            (dt.time(hour=9), dt.time(hour=9)),
            (dt.time(hour=8, minute=30), dt.time(hour=9)),
            (dt.time(hour=9), dt.time(hour=8, minute=30)),
        ],
    )
    def test_filter_for_clashes_gives_clash(self, break_starts_at, period_starts_at):
        """Test that a slot and break at the exact same time clash."""
        # The break and slot are both 1 hour long, defined according to parameters
        break_ = factories.Break(
            break_starts_at=break_starts_at,
            break_ends_at=dt.time(
                hour=(break_starts_at.hour + 1), minute=break_starts_at.minute
            ),
        )
        slot = factories.TimetableSlot(
            school=break_.school,
            period_starts_at=period_starts_at,
            period_ends_at=dt.time(
                hour=(period_starts_at.hour + 1), minute=period_starts_at.minute
            ),
        )

        # Get clashes and check break in them
        clashes = models.Break.objects.filter_for_clashes(slot)

        assert clashes.count() == 1
        assert break_ in clashes

    @pytest.mark.parametrize("break_starts_at", [dt.time(hour=9), dt.time(hour=10)])
    def test_filter_for_clashes_break_at_different_time_to_slot_gives_no_clashes(
        self, break_starts_at
    ):
        """Test that a slot and break at different times don't clash."""
        # Make a break and slot at different times
        break_ = factories.Break(
            break_starts_at=break_starts_at,
            break_ends_at=dt.time(
                hour=(break_starts_at.hour + 1), minute=break_starts_at.minute
            ),
        )
        slot = factories.TimetableSlot(
            school=break_.school,
            period_starts_at=dt.time(hour=8),
            period_ends_at=dt.time(hour=9),
        )

        # Get clashes and check break in them
        clashes = models.Break.objects.filter_for_clashes(slot)

        assert clashes.count() == 0


@pytest.mark.django_db
class TestBreak:
    """
    Unit tests for the Break model.
    """

    # --------------------
    # Factories tests
    # --------------------

    def test_create_new_for_valid_break(self):
        """
        Test we can create a valid Break instance using create_new()
        """
        # Get some teachers and year groups to add
        school = factories.School()
        teacher = factories.Teacher()
        yg = factories.YearGroup()

        # Make the break
        break_ = models.Break.create_new(
            school_id=school.school_access_key,
            break_id="1",
            break_name="Morning break",
            break_starts_at=dt.time(hour=11, minute=30),
            break_ends_at=dt.time(hour=12),
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

    def test_create_new_for_invalid_break_id_already_taken(self):
        """
        Test we can cannot create two breaks with the same ID at a school.
        """
        # Make a break to block uniqueness
        break_ = factories.Break()

        # Try to make another break with the same id
        with pytest.raises(IntegrityError):
            models.Break.create_new(
                school_id=break_.school.school_access_key,
                break_id=break_.break_id,
                break_name="test",
                break_starts_at=dt.time(hour=11, minute=30),
                break_ends_at=dt.time(hour=12),
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.none(),
                relevant_year_groups=models.YearGroup.objects.none(),
            )

    def test_delete_all_breaks_for_school_successful(self):
        """
        Test that we can delete all the breaks associated with a school.
        """
        # Make a break
        break_ = factories.Break()

        # Try deleting the break
        models.Break.delete_all_breaks_for_school(
            school_id=break_.school.school_access_key
        )

        # Check break was deleted
        assert models.Break.objects.count() == 0
