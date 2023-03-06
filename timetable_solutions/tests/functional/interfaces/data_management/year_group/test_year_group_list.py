"""Tests for the year group list view in the data management app."""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestYearGroupList(TestClient):
    def test_loads_all_year_groups_for_school(self):
        # Create a school and authorise the test client for this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some year group data for the school
        yg_1 = data_factories.YearGroup(year_group_id=1, school=school)
        yg_2 = data_factories.YearGroup(year_group_id=2, school=school)

        # Create a year group at some other school
        data_factories.YearGroup()

        # Navigate to the year group list view
        url = UrlName.YEAR_GROUP_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            serializers_helpers.expected_year_group(yg_1),
            serializers_helpers.expected_year_group(yg_2),
        ]
