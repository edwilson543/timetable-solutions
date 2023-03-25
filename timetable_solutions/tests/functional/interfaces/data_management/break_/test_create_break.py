"""
Tests for creating a new break.
"""

# Standard library imports
import datetime as dt

# Local application imports
from data import constants, models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestBreakCreate(TestClient):
    def test_valid_create_break_form_creates_break_in_db(self):
        # Create existing db content
        school = data_factories.School()

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.BREAK_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]

        # Fill out and submit the form
        form["break_id"] = "my-break"
        form["break_name"] = "monday-morning"
        form["day_of_week"] = constants.Day.MONDAY
        form["starts_at"] = dt.time(hour=9)
        form["ends_at"] = dt.time(hour=10)
        form["relevant_to_all_year_groups"] = False

        response = form.submit()

        # Check response ok and redirects
        assert response.status_code == 302
        assert response.location == UrlName.BREAK_LIST.url()

        # Check a new break_ was created in the db
        break_ = models.Break.objects.get()
        assert break_.break_id == "my-break"
        assert break_.break_name == "monday-morning"
        assert break_.day_of_week == constants.Day.MONDAY
        assert break_.starts_at == dt.time(hour=9)
        assert break_.ends_at == dt.time(hour=10)

    def test_creating_break_with_invalid_start_and_end_time_fails(self):
        school = data_factories.School()

        self.authorise_client_for_school(school)
        url = UrlName.BREAK_CREATE.url()
        page = self.client.get(url)
        form = page.forms["create-form"]

        # Fill the form and put the end time before the start time
        form["break_id"] = "some-break"
        form["break_name"] = "some-break"
        form["day_of_week"] = constants.Day.MONDAY
        form["starts_at"] = dt.time(hour=9)
        form["ends_at"] = dt.time(hour=8)

        form_response = form.submit()

        # Check response ok
        assert form_response.status_code == 200

        django_form = form_response.context["form"]
        errors = django_form.errors.as_text()
        assert "The break must end after it has started!" in errors

        # Check no break_ was created
        assert models.Break.objects.count() == 0
