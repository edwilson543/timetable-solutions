"""
Tests for the page allowing users to delete individual pupils.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestPupilDelete(TestClient):
    def test_successfully_deletes_pupil(self):
        pupil = data_factories.Pupil()
        self.authorise_client_for_school(pupil.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.PUPIL_UPDATE.url(pupil_id=pupil.pupil_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok and pupil was deleted
        assert delete_response.status_code == 302
        assert delete_response.location == UrlName.PUPIL_LIST.url()

        assert not models.Pupil.objects.exists()
