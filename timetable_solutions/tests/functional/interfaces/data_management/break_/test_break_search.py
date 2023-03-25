"""
Tests for the break search view in the data management app.
"""

# Standard library imports
from unittest import mock

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import views
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestBreakSearch(TestClient):
    def test_loads_all_breaks_for_school_then_filters_by_search_term(self):
        # Create a school and authorise the test client for this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some data for the school
        yg = data_factories.YearGroup(school=school)
        break_a = data_factories.Break(
            break_id="aaa", school=school, relevant_year_groups=(yg,)
        )
        break_b = data_factories.Break(break_id="bbb", school=school)

        # Create a break_ at some other school
        data_factories.Break()

        # Navigate to the break_ search view
        url = UrlName.BREAK_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            serializers_helpers.expected_break(break_a),
            serializers_helpers.expected_break(break_b),
        ]

        django_form = response.context["form"]
        assert not django_form.errors

        # Retrieve the html form and submit a valid search term
        webtest_form = response.forms["search-form"]
        webtest_form["year_group"] = yg.id

        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok and search results
        assert search_response.status_code == 200

        breaks = search_response.context["page_obj"].object_list
        assert breaks == [serializers_helpers.expected_break(break_a)]

        # The form should be populated with the existing search
        webtest_form = search_response.forms["search-form"]
        assert webtest_form["search_term"].value == ""
        assert webtest_form["year_group"].value == str(yg.id)

    @mock.patch.object(views.BreakSearch, "paginate_by", 1)
    def test_loads_paginated_breaks_then_form_invalid_because_no_search_term(
        self,
    ):
        # Create a school and authorise the test client to this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some break_ data for our school
        break_a = data_factories.Break(break_id="aaa", school=school)
        break_b = data_factories.Break(break_id="bbb", school=school)

        # Navigate to the break_ search view
        url = UrlName.BREAK_LIST.url()
        response = self.client.get(url)

        # Check response ok
        assert response.status_code == 200

        # Check the breaks have been paginated across two pages
        page_1 = response.context["page_obj"]
        assert page_1.object_list == [serializers_helpers.expected_break(break_a)]
        assert page_1.has_next()

        paginator = response.context["paginator"]
        assert paginator.object_list == [
            serializers_helpers.expected_break(break_a),
            serializers_helpers.expected_break(break_b),
        ]

        # Retrieve the html form and submit an empty search term
        webtest_form = response.forms["search-form"]
        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok
        assert search_response.status_code == 200

        # Form should show errors
        django_form = search_response.context["form"]
        assert django_form.errors.as_text()

        # The full break_ list should still be shown
        page_1 = search_response.context["page_obj"]
        assert page_1.object_list == [serializers_helpers.expected_break(break_a)]
        assert page_1.has_next()
