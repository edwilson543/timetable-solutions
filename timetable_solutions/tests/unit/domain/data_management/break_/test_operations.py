"""Unit tests for Break model operations"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants, models
from domain.data_management.break_ import exceptions, operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewBreak:
    def test_create_new_for_valid_break(self):
        # Get some teachers and year groups to add
        school = data_factories.School()
        data_factories.Teacher(school=school)
        data_factories.YearGroup(school=school)

        # Make the break
        break_ = operations.create_new_break(
            school_id=school.school_access_key,
            break_id="1",
            break_name="Morning break",
            starts_at=dt.time(hour=11, minute=30),
            ends_at=dt.time(hour=12),
            day_of_week=constants.Day.MONDAY,
            teachers=models.Teacher.objects.all(),
            relevant_year_groups=models.YearGroup.objects.all(),
        )

        # Check break in db and defined as expected
        assert break_ == models.Break.objects.get()

        assert break_.school == school
        assert break_.break_id == "1"
        assert break_.break_name
        assert break_.teachers.get() == models.Teacher.objects.get()
        assert break_.relevant_year_groups.get() == models.YearGroup.objects.get()

    def test_raises_when_break_id_already_taken(self):
        break_ = data_factories.Break()

        # Try to make another break with the same id
        with pytest.raises(exceptions.CouldNotCreateBreak):
            operations.create_new_break(
                school_id=break_.school.school_access_key,
                break_id=break_.break_id,
                break_name="Morning break",
                starts_at=dt.time(hour=11, minute=30),
                ends_at=dt.time(hour=12),
                day_of_week=constants.Day.MONDAY,
                teachers=models.Teacher.objects.all(),
                relevant_year_groups=models.YearGroup.objects.all(),
            )
