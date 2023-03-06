"""Unit tests for year group operations"""

# Third party imports
import pytest

# Local application imports
from data import models
from domain.data_management.year_groups import exceptions, operations
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewYearGroup:
    @pytest.mark.parametrize("year_group_id", [1, None])
    def test_creates_year_group_in_db_for_valid_params(self, year_group_id: int | None):
        # Make a school for the year group
        school = data_factories.School()

        # Try creating year group
        operations.create_new_year_group(
            school_id=school.school_access_key,
            year_group_id=year_group_id,
            year_group_name="test",
        )

        # Check year group was created
        all_ygs = models.YearGroup.objects.all()
        yg = all_ygs.get()

        assert yg.year_group_id == 1
        assert yg.year_group_name == "test"

    def test_raises_when_year_group_id_not_unique_for_school(self):
        # Make a year group to occupy an id value
        yg = data_factories.YearGroup()
        school = yg.school

        # Try making a year group with the same school / id
        with pytest.raises(exceptions.CouldNotCreateYearGroup):
            operations.create_new_year_group(
                school_id=school.school_access_key,
                year_group_id=yg.year_group_id,
                year_group_name="test",
            )

    def test_raises_when_year_group_id_given_as_string(self):
        school = data_factories.School()

        with pytest.raises(exceptions.CouldNotCreateYearGroup):
            operations.create_new_year_group(
                school_id=school.school_access_key,
                year_group_id="not-an-integer",
                year_group_name="test",
            )
