"""
Tests for creating a timetable slot.
"""

# Standard library imports
import datetime as dt

# Local application imports
from data import constants, models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestTimetableSlotCreate(TestClient):
    def test_valid_create_slot_form_creates_slot_in_db(self):
        # Create existing db content
        school = data_factories.School()
        slot = data_factories.TimetableSlot(school=school)
        new_slot_id = slot.slot_id + 1

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.TIMETABLE_SLOT_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]
        # Suggested value for the slot id should be one more than next highest
        assert int(form["slot_id"].value) == new_slot_id

        # Fill out and submit the form
        form["slot_id"] = new_slot_id
        form["day_of_week"] = constants.Day.MONDAY
        form["starts_at"] = dt.time(hour=9)
        form["ends_at"] = dt.time(hour=10)
        form["relevant_to_all_year_groups"] = False

        response = form.submit()

        # Check response ok and redirects
        assert response.status_code == 302
        assert response.location == UrlName.TIMETABLE_SLOT_LIST.url()

        # Check a new slot was created in the db
        slot = models.TimetableSlot.objects.get(
            school_id=school.school_access_key, slot_id=new_slot_id
        )
        assert slot.slot_id == new_slot_id
        assert slot.day_of_week == constants.Day.MONDAY
        assert slot.starts_at == dt.time(hour=9)
        assert slot.ends_at == dt.time(hour=10)

    def test_creating_slot_with_invalid_start_and_end_time_fails(self):
        # Create a slot whose ID will try to create a new slot with
        school = data_factories.School()

        self.authorise_client_for_school(school)
        url = UrlName.TIMETABLE_SLOT_CREATE.url()
        page = self.client.get(url)
        form = page.forms["create-form"]

        # Fill the form and put the end time before the start time
        form["slot_id"] = 1
        form["day_of_week"] = constants.Day.MONDAY
        form["starts_at"] = dt.time(hour=9)
        form["ends_at"] = dt.time(hour=8)

        form_response = form.submit()

        # Check response ok
        assert form_response.status_code == 200

        django_form = form_response.context["form"]
        errors = django_form.errors.as_text()
        assert "The slot must end after it has started!" in errors

        # Check no slot was created
        assert models.TimetableSlot.objects.count() == 0
