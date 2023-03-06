"""Queries related to managing year group data."""

# Third party imports
import pytest

# Local application imports
from domain.data_management.year_groups import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetYearGroupForSchool:
    def test_gets_year_group(self):
        yg = data_factories.YearGroup()

        got_yg = queries.get_year_group_for_school(
            school_id=yg.school.school_access_key, year_group_id=yg.year_group_id
        )

        assert got_yg == yg

    def test_gets_none_when_year_group_doesnt_exist(self):
        school = data_factories.School()

        yg = queries.get_year_group_for_school(
            school_id=school.school_access_key, year_group_id=1
        )

        assert yg is None


@pytest.mark.django_db
class TestGetNextIdForSchool:
    def test_gets_next_year_group_id_when_school_has_year_groups(self):
        school = data_factories.School()
        yg_a = data_factories.YearGroup(school=school)
        yg_b = data_factories.YearGroup(school=school)

        next_id = queries.get_next_year_group_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == max(yg_a.year_group_id, yg_b.year_group_id) + 1

    def test_gets_one_when_school_has_no_year_groups(self):
        school = data_factories.School()

        next_id = queries.get_next_year_group_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == 1
