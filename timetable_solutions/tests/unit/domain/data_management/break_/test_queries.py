"""
Tests for queries related to managing break_ data.
"""

# Third party imports
import pytest

# Local application imports
from data import constants
from domain.data_management.break_ import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetBreak:
    @pytest.mark.parametrize("search_field", ["break_id", "break_name"])
    def test_gets_break_matching_id_or_name(self, search_field: str):
        break_ = data_factories.Break(break_id=1, break_name="Test")

        # This break_ will not match the search term
        data_factories.Break(
            school=break_.school, break_id=2, break_name="Somthing else"
        )
        # This break is for a different school
        data_factories.Break(break_id=1)

        search_term = getattr(break_, search_field)
        breaks = queries.get_breaks(
            school_id=break_.school.school_access_key, search_term=search_term
        )

        assert breaks.get() == break_

    def test_gets_break_matching_day(self):
        break_ = data_factories.Break(day_of_week=constants.Day.MONDAY)

        # This break_ will not match the day of the week
        data_factories.Break(school=break_.school, day_of_week=constants.Day.TUESDAY)
        # This break_ will be for a different school
        data_factories.Break(day_of_week=constants.Day.MONDAY)

        breaks = queries.get_breaks(
            school_id=break_.school.school_access_key, day=break_.day_of_week
        )

        assert breaks.get() == break_

    def test_gets_break_matching_year_group(self):
        yg = data_factories.YearGroup()
        break_ = data_factories.Break(school=yg.school, relevant_year_groups=(yg,))

        # This break_ will not be associated with the relevant year group
        data_factories.Break(school=break_.school)

        breaks = queries.get_breaks(
            school_id=break_.school.school_access_key, year_group=yg
        )

        assert breaks.get() == break_

    def test_gets_break_matching_multiple_parameters(self):
        break_ = data_factories.Break()

        # The second break_ will be for a different school
        data_factories.Break(break_id=break_.break_id, day_of_week=break_.day_of_week)

        breaks = queries.get_breaks(
            school_id=break_.school.school_access_key,
            search_term=break_.break_id,
            day=break_.day_of_week,
        )

        assert breaks.get() == break_
