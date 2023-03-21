"""
Tests for the page allowing users to delete individual timetable slots.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestTimetableSlotDelete(TestClient):
    def test_successfully_deletes_slot(self):
        slot = data_factories.TimetableSlot()
        self.authorise_client_for_school(slot.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=slot.slot_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok and slot was deleted
        assert delete_response.status_code == 302
        assert delete_response.location == UrlName.TIMETABLE_SLOT_LIST.url()

        assert not models.TimetableSlot.objects.exists()
