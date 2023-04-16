"""
Tests for the pupil landing page in the data management app.
"""

# Third party imports
import pytest

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestPupilLanding(TestClient):
    @pytest.mark.parametrize(
        "has_existing_data,can_add_data", [(True, True), (False, True), (False, False)]
    )
    def test_landing_page_loads_when_has_data(
        self, has_existing_data: bool, can_add_data: bool
    ):
        """
        Test that an authenticated user can access the pupil landing page,
        and click through to the relevant sections of pupil data management.
        """
        # Authorise the client for some school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Set database state according to test parameters
        if has_existing_data:
            data_factories.Pupil(school=school)
        if can_add_data:
            data_factories.YearGroup(school=school)

        # Navigate to the pupil landing page
        url = UrlName.PUPIL_LANDING_PAGE.url()
        response = self.client.get(url)

        # Check the page loaded
        assert response.status_code == 200

        assert response.context["create_url"] == UrlName.PUPIL_CREATE.url()
        assert response.context["upload_url"] == UrlName.PUPIL_UPLOAD.url()
        assert response.context["list_url"] == UrlName.PUPIL_LIST.url()

        # If the user has data, they should be able to click through to this data
        no_data_alert = response.html.find("div", {"id": "no-data-alert"})
        if has_existing_data:
            assert not no_data_alert
        else:
            assert no_data_alert

        # If the user can add data, they should be able to click through to create / upload it
        if can_add_data:
            response.click(href=UrlName.PUPIL_CREATE.url())
            response.click(href=UrlName.PUPIL_UPLOAD.url())
        else:
            with pytest.raises(IndexError):
                response.click(href=UrlName.PUPIL_CREATE.url())
            with pytest.raises(IndexError):
                response.click(href=UrlName.PUPIL_UPLOAD.url())

    def test_anonymous_user_redirected(self):
        # Try to access landing page with an anonymous user
        self.anonymize_user()
        url = UrlName.PUPIL_LANDING_PAGE.url()
        response = self.client.get(url)

        # Check user is redirected to login page
        assert response.status_code == 302
        assert "users/accounts/login" in response.url
