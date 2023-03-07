"""Tests for updating year group details via the YearGroupUpdate view."""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestYearGroupUpdate(TestClient):
    def test_access_detail_page_with_disabled_form(self):
        # Make a year_group's data to access
        yg = data_factories.YearGroup()
        self.authorise_client_for_school(yg.school)

        # Navigate to this year_group's detail view
        url = UrlName.YEAR_GROUP_UPDATE.url(year_group_id=yg.year_group_id)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        assert page.context[
            "serialized_model_instance"
        ] == serializers_helpers.expected_year_group(yg)

        # Check the initial form values match the year_group's
        form = page.forms["disabled-change-form"]
        assert form["year_group_name"].value == yg.year_group_name

    def test_hx_get_enables_form_then_valid_details_submitted(self):
        # Make a year_group's data to access
        yg = data_factories.YearGroup()
        self.authorise_client_for_school(yg.school)

        # Navigate to this year_group's detail view
        url = UrlName.YEAR_GROUP_UPDATE.url(year_group_id=yg.year_group_id)
        htmx_headers = {"HTTP_HX-Request": "true"}
        form_partial = self.client.get(url, headers=htmx_headers)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]
        assert form["year_group_name"].value == yg.year_group_name

        # Fill in and post the form
        form["year_group_name"] = "Year 100"

        response = form.submit(name="update-submit")

        # Check response ok and year_group details updated
        assert response.status_code == 302
        assert response.location == url

        yg.refresh_from_db()
        assert yg.year_group_name == "Year 100"
