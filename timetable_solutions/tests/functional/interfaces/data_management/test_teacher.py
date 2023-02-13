"""Tests for the teacher data management views."""

from django.contrib.auth import models as auth_models
from django import test
import pytest

from interfaces.constants import UrlName
from tests import data_factories


@pytest.mark.django_db
class TestTeacherLanding:
    @pytest.mark.parametrize("has_existing_data", [True, False])
    def test_landing_page_loads(self, has_existing_data: bool):
        """
        Smoke test that a logged-in user can access the teacher landing page.

        The markup is slightly different depending on whether they have existing data,
        so test both cases.
        """
        # Create a user and log them in
        user = auth_models.User.objects.create_user(
            username="testing", password="unhashed"
        )
        profile = data_factories.Profile(user=user)
        if has_existing_data:
            data_factories.Teacher(school=profile.school)
        client = test.Client()
        client.login(username=user.username, password="unhashed")

        # Navigate to the teacher landing page
        url = UrlName.TEACHERS_LANDING_PAGE.url()
        response = client.get(url)

        # Check the page loaded
        assert response.status_code == 200

    def test_anonymous_user_redirected(self):
        # Try to access landing page with an anonymous user
        client = test.Client()
        url = UrlName.TEACHERS_LANDING_PAGE.url()
        response = client.get(url)

        # Check user is redirected to login page
        assert response.status_code == 302
        assert "users/accounts/login" in response.url
