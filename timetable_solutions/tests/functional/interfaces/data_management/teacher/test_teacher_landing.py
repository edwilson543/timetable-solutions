"""
Tests for the teacher landing page in the data management app.
"""

# Third party imports
import pytest

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestTeacherLanding(TestClient):
    @pytest.mark.parametrize("has_existing_data", [True, False])
    def test_landing_page_loads(self, has_existing_data: bool):
        """
        Test that an authenticated user can access the teacher landing page,
        and click through to view this data.
        """
        # Authorise the client for some school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        if has_existing_data:
            data_factories.Teacher(school=school)

        # Navigate to the teacher landing page
        url = UrlName.TEACHER_LANDING_PAGE.url()
        response = self.client.get(url)

        # Check the page loaded
        assert response.status_code == 200

        assert response.context["create_url"] == UrlName.TEACHER_CREATE.url()
        assert response.context["upload_url"] == UrlName.TEACHER_UPLOAD.url()
        assert response.context["list_url"] == UrlName.TEACHER_LIST.url()

        # If the user has data, they should be able to click through to this data
        no_data_alert = response.html.find("div", {"id": "no-data-alert"})
        if has_existing_data:
            assert not no_data_alert
        else:
            assert no_data_alert

    def test_anonymous_user_redirected(self):
        # Try to access landing page with an anonymous user
        self.anonymize_user()
        url = UrlName.TEACHER_LANDING_PAGE.url()
        response = self.client.get(url)

        # Check user is redirected to login page
        assert response.status_code == 302
        assert "users/accounts/login" in response.url
