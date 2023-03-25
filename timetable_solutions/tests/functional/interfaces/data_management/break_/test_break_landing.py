"""
Tests for the break landing page in the data management app.
"""

# Third party imports
import pytest

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestBreakLanding(TestClient):
    @pytest.mark.parametrize(
        "has_existing_data,has_year_group_data,has_teacher_data",
        [
            (True, True, True),
            (False, True, False),
            (False, False, True),
            (False, False, False),
        ],
    )
    def test_landing_page_loads_when_has_data(
        self, has_existing_data: bool, has_year_group_data: bool, has_teacher_data: bool
    ):
        """
        Test that an authenticated user can access the break landing page,
        and click through to the relevant sections of break data management.
        """
        # Authorise the client for some school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Set database state according to test parameters
        can_add_data = has_year_group_data and has_teacher_data
        if has_existing_data:
            data_factories.Break(school=school)
        if has_year_group_data:
            data_factories.YearGroup(school=school)
        if has_teacher_data:
            data_factories.Teacher(school=school)

        # Navigate to the break_ landing page
        url = UrlName.BREAK_LANDING_PAGE.url()
        response = self.client.get(url)

        # Check the page loaded
        assert response.status_code == 200

        assert response.context["create_url"] == UrlName.BREAK_CREATE.url()
        assert response.context["upload_url"] == UrlName.BREAK_UPLOAD.url()
        assert response.context["list_url"] == UrlName.BREAK_LIST.url()

        # If the user has data, they should be able to click through to this data
        if has_existing_data:
            response.click(href=UrlName.BREAK_LIST.url())
        else:
            with pytest.raises(IndexError):
                response.click(href=UrlName.BREAK_LIST.url())

        # If the user can add data, they should be able to click through to create / upload it
        if can_add_data:
            response.click(href=UrlName.BREAK_CREATE.url())
            response.click(href=UrlName.BREAK_UPLOAD.url())
        else:
            with pytest.raises(IndexError):
                response.click(href=UrlName.BREAK_CREATE.url())
            with pytest.raises(IndexError):
                response.click(href=UrlName.BREAK_UPLOAD.url())

    def test_anonymous_user_redirected(self):
        # Try to access landing page with an anonymous user
        self.anonymize_user()
        url = UrlName.BREAK_LANDING_PAGE.url()
        response = self.client.get(url)

        # Check user is redirected to login page
        assert response.status_code == 302
        assert "users/accounts/login" in response.url
