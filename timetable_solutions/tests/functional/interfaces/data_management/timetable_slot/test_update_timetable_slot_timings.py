"""
Tests for updating slot timings via the TimetableSlotUpdate view.
"""

# Standard library imports
import datetime as dt

# Local application imports
from data import constants
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestTimetableSlotUpdate(TestClient):
    def test_access_detail_page_with_disabled_form(self):
        # Make a slot's data to access
        slot = data_factories.TimetableSlot(
            starts_at=dt.time(hour=8), ends_at=dt.time(hour=9)
        )
        self.authorise_client_for_school(slot.school)

        # Navigate to this slot's detail view
        url = UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=slot.slot_id)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        assert page.context[
            "serialized_model_instance"
        ] == serializers_helpers.expected_slot(slot)

        # Check the initial form values match the slot's
        form = page.forms["disabled-update-form"]
        assert form["day_of_week"].value == str(slot.day_of_week)
        assert form["starts_at"].value == "08:00"
        assert form["ends_at"].value == "09:00"

    def test_hx_get_enables_form_then_valid_details_submitted(self):
        # Make a slot's data to access
        slot = data_factories.TimetableSlot(
            starts_at=dt.time(hour=17), ends_at=dt.time(hour=17, minute=45)
        )
        self.authorise_client_for_school(slot.school)

        # Navigate to this slot's detail view
        url = UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=slot.slot_id)
        htmx_headers = {"HX-Request": "true"}
        form_partial = self.client.get(url, headers=htmx_headers)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]
        assert form["day_of_week"].value == str(slot.day_of_week)
        assert form["starts_at"].value == "17:00"
        assert form["ends_at"].value == "17:45"

        # Fill in and post the form
        form["day_of_week"] = constants.Day.MONDAY.value
        form["starts_at"] = dt.time(hour=9)
        form["ends_at"] = dt.time(hour=10, minute=30)

        response = form.submit(name="update-submit")

        # Check response ok and slot details updated
        assert response.status_code == 302
        assert response.location == url

        slot.refresh_from_db()
        assert slot.day_of_week == constants.Day.MONDAY
        assert slot.starts_at == dt.time(hour=9)
        assert slot.ends_at == dt.time(hour=10, minute=30)

    def test_updating_slot_leading_to_a_clash_for_a_year_group_fails(self):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make a year group and two slots
        # The first slot will be updated to clash with the second
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )
        next_slot = data_factories.TimetableSlot(
            school=school,
            relevant_year_groups=(yg,),
            starts_at=dt.time(hour=10),
            ends_at=dt.time(hour=10, minute=30),
        )

        # Navigate to the first slot's detail view
        url = UrlName.TIMETABLE_SLOT_UPDATE.url(slot_id=slot.slot_id)
        htmx_headers = {"HX-Request": "true"}
        form_partial = self.client.get(url, headers=htmx_headers)

        # Check response ok
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]

        # Fill in and post the form
        form["day_of_week"] = next_slot.day_of_week
        form["starts_at"] = dt.time(hour=9)
        form["ends_at"] = dt.time(hour=10, minute=30)

        response = form.submit(name="update-submit")

        # Check response ok
        assert response.status_code == 200

        # Check for relevant error message and slot not updated
        django_form = response.context["form"]
        error_message = django_form.errors.as_text()
        assert "at least one of its assigned year groups has a " in error_message
        assert "slot" in error_message

        slot.refresh_from_db()
        assert slot.starts_at != next_slot.starts_at
        assert slot.ends_at != next_slot.ends_at
