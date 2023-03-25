"""
Tests for the page allowing users to delete individual breaks.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestBreakDelete(TestClient):
    def test_successfully_deletes_break(self):
        break_ = data_factories.Break()
        self.authorise_client_for_school(break_.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.BREAK_UPDATE.url(break_id=break_.break_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok and break_ was deleted
        assert delete_response.status_code == 302
        assert delete_response.location == UrlName.BREAK_LIST.url()

        assert not models.Break.objects.exists()
