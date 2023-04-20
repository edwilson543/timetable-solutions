"""
Tests for the page allowing admin users to delete other users.
"""

# Third party imports
import pytest

# Django imports
from django.contrib.auth import models as auth_models

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestUserProfileDelete(TestClient):
    def test_successfully_deletes_user_and_associated_profile(self):
        profile = data_factories.Profile()
        user = profile.user
        self.authorise_client_for_school(profile.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.USER_UPDATE.url(username=user.username)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok and year group was deleted
        assert delete_response.status_code == 302
        assert delete_response.location == UrlName.USER_LIST.url()

        with pytest.raises(models.Profile.DoesNotExist):
            profile.refresh_from_db()

        with pytest.raises(auth_models.User.DoesNotExist):
            user.refresh_from_db()
