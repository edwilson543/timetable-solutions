"""Tests for the year group landing page in the data management app."""

# Third party imports
import pytest

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestYearGroupLanding(TestClient):
    @pytest.mark.parametrize("has_existing_data", [True, False])
    def test_landing_page_loads(self, has_existing_data: bool):
        """
        Smoke test that a logged-in user can access the year group landing page.

        The markup is slightly different depending on whether they have existing data,
        so test both cases.
        """
        # Authorise the client for some school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        if has_existing_data:
            data_factories.YearGroup(school=school)

        # Navigate to the year group landing page
        url = UrlName.YEAR_GROUP_LANDING_PAGE.url()
        response = self.client.get(url)

        # Check the page loaded
        assert response.status_code == 200

        # TODO -> update the urls once implemented
        assert response.context["create_url"] == UrlName.YEAR_GROUP_CREATE.url()
        assert response.context["upload_url"] == UrlName.TEACHER_UPLOAD.url()
        assert response.context["list_url"] == UrlName.YEAR_GROUP_LIST.url()

    def test_anonymous_user_redirected(self):
        # Try to access landing page with an anonymous user
        self.anonymize_user()
        url = UrlName.YEAR_GROUP_LANDING_PAGE.url()
        response = self.client.get(url)

        # Check user is redirected to login page
        assert response.status_code == 302
        assert "users/accounts/login" in response.url
