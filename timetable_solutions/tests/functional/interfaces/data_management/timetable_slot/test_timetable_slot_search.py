"""
Tests for the slot search view in the data management app.
"""

# Standard library imports
from unittest import mock

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import views
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestTimetableSlotSearch(TestClient):
    def test_loads_all_slots_for_school_then_filters_by_search_term(self):
        # Create a school and authorise the test client for this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some data for the school
        yg = data_factories.YearGroup(school=school)
        slot_1 = data_factories.TimetableSlot(
            slot_id=1, school=school, relevant_year_groups=(yg,)
        )
        slot_2 = data_factories.TimetableSlot(slot_id=2, school=school)

        # Create a slot at some other school
        data_factories.TimetableSlot()

        # Navigate to the slot search view
        url = UrlName.TIMETABLE_SLOT_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            serializers_helpers.expected_slot(slot_1),
            serializers_helpers.expected_slot(slot_2),
        ]

        django_form = response.context["form"]
        assert not django_form.errors

        # Retrieve the html form and submit a valid search term
        webtest_form = response.forms["search-form"]
        webtest_form["year_group"] = yg.id

        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok and search results
        assert search_response.status_code == 200

        slots = search_response.context["page_obj"].object_list
        assert slots == [serializers_helpers.expected_slot(slot_1)]

        # The form should be populated with the existing search
        webtest_form = search_response.forms["search-form"]
        assert webtest_form["slot_id"].value == ""
        assert webtest_form["year_group"].value == str(yg.id)

    @mock.patch.object(views.TimetableSlotSearch, "paginate_by", 1)
    def test_loads_paginated_slots_then_form_invalid_because_searched_slot_id_has_no_slot(
        self,
    ):
        # Create a school and authorise the test client to this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some slot data for our school
        slot_1 = data_factories.TimetableSlot(slot_id=1, school=school)
        slot_2 = data_factories.TimetableSlot(slot_id=2, school=school)

        # Navigate to the slot search view
        url = UrlName.TIMETABLE_SLOT_LIST.url()
        response = self.client.get(url)

        # Check response ok
        assert response.status_code == 200

        # Check the slots have been paginated across two pages
        page_1 = response.context["page_obj"]
        assert page_1.object_list == [serializers_helpers.expected_slot(slot_1)]
        assert page_1.has_next()

        paginator = response.context["paginator"]
        assert paginator.object_list == [
            serializers_helpers.expected_slot(slot_1),
            serializers_helpers.expected_slot(slot_2),
        ]

        # Retrieve the html form and submit a search for a non-existent slot id
        webtest_form = response.forms["search-form"]
        invalid_id = slot_1.slot_id + slot_2.slot_id
        webtest_form["slot_id"] = invalid_id
        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok
        assert search_response.status_code == 200

        # Form should show errors
        django_form = search_response.context["form"]
        assert (
            f"No timetable slot with id: {invalid_id} exists!"
            in django_form.errors.as_text()
        )

        # The full slot list should still be shown
        page_1 = search_response.context["page_obj"]
        assert page_1.object_list == [serializers_helpers.expected_slot(slot_1)]
        assert page_1.has_next()
