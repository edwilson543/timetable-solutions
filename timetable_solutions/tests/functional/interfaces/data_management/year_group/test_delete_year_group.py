"""Tests for the page allowing users to delete individual year groups."""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestYearGroupDelete(TestClient):
    def test_successfully_deletes_year_group(self):
        yg = data_factories.YearGroup()
        self.authorise_client_for_school(yg.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.YEAR_GROUP_UPDATE.url(year_group_id=yg.year_group_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok and year group was deleted
        assert delete_response.status_code == 302
        assert delete_response.location == UrlName.YEAR_GROUP_LIST.url()

        assert not models.YearGroup.objects.exists()
