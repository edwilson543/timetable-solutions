"""
Tests for updating break timings via the BreakUpdate view.
"""

# Standard library imports
import datetime as dt

# Local application imports
from data import constants
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestBreakUpdate(TestClient):
    def test_access_detail_page_with_disabled_form(self):
        # Make a break_'s data to access
        break_ = data_factories.Break(
            starts_at=dt.time(hour=8), ends_at=dt.time(hour=9)
        )
        self.authorise_client_for_school(break_.school)

        # Navigate to this break_'s detail view
        url = UrlName.BREAK_UPDATE.url(break_id=break_.break_id)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        assert page.context[
            "serialized_model_instance"
        ] == serializers_helpers.expected_break(break_)

        # Check the initial form values match the break_'s
        form = page.forms["disabled-update-form"]
        assert form["day_of_week"].value == str(break_.day_of_week)
        assert form["starts_at"].value == "08:00"
        assert form["ends_at"].value == "09:00"

    def test_hx_get_enables_form_then_valid_details_submitted(self):
        # Make a break's data to access
        break_ = data_factories.Break(
            starts_at=dt.time(hour=17), ends_at=dt.time(hour=17, minute=45)
        )
        self.authorise_client_for_school(break_.school)

        # Navigate to this break's detail view
        url = UrlName.BREAK_UPDATE.url(break_id=break_.break_id)
        form_partial = self.hx_get(url)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]
        assert form["break_name"].value == break_.break_name
        assert form["day_of_week"].value == str(break_.day_of_week)
        assert form["starts_at"].value == "17:00"
        assert form["ends_at"].value == "17:45"

        # Fill in and post the form
        form["day_of_week"] = constants.Day.MONDAY.value
        form["starts_at"] = dt.time(hour=9)
        form["ends_at"] = dt.time(hour=10, minute=30)

        response = form.submit(name="update-submit")

        # Check response ok and break_ details updated
        assert response.status_code == 302
        assert response.location == url

        break_.refresh_from_db()
        assert break_.day_of_week == constants.Day.MONDAY
        assert break_.starts_at == dt.time(hour=9)
        assert break_.ends_at == dt.time(hour=10, minute=30)

    def test_updating_break_leading_to_a_clash_for_a_year_group_fails(self):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make a year group and two breaks
        # The first break_ will be updated to clash with the second
        yg = data_factories.YearGroup(school=school)
        break_ = data_factories.Break(
            school=school,
            relevant_year_groups=(yg,),
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
        )
        next_break_ = data_factories.Break(
            school=school,
            relevant_year_groups=(yg,),
            starts_at=dt.time(hour=10),
            ends_at=dt.time(hour=10, minute=30),
        )

        # Navigate to the first break_'s detail view
        url = UrlName.BREAK_UPDATE.url(break_id=break_.break_id)
        form_partial = self.hx_get(url)

        # Check response ok
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]

        # Fill in and post the form
        form["day_of_week"] = next_break_.day_of_week
        form["starts_at"] = dt.time(hour=9)
        form["ends_at"] = dt.time(hour=10, minute=30)

        response = form.submit(name="update-submit")

        # Check response ok
        assert response.status_code == 200

        # Check for relevant error message and break_ not updated
        django_form = response.context["form"]
        error_message = django_form.errors.as_text()
        assert "at least one of its assigned year groups has a " in error_message
        assert "break" in error_message

        break_.refresh_from_db()
        assert break_.starts_at != next_break_.starts_at
        assert break_.ends_at != next_break_.ends_at
