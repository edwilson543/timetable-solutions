"""
Tests for the pupil search view in the data management app.
"""

# Standard library imports
from unittest import mock

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import views
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestPupilSearch(TestClient):
    def test_loads_all_pupils_for_school_then_filters_by_search_term(self):
        # Create a school and authorise the test client for this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some pupil data for the school
        pupil_1 = data_factories.Pupil(pupil_id=1, school=school)
        pupil_2 = data_factories.Pupil(pupil_id=2, school=school)

        # Create a pupil at some other school
        data_factories.Pupil()

        # Navigate to the pupil search view
        url = UrlName.PUPIL_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            serializers_helpers.expected_pupil(pupil_1),
            serializers_helpers.expected_pupil(pupil_2),
        ]

        django_form = response.context["form"]
        assert not django_form.errors

        # Retrieve the html form and submit a valid search term
        webtest_form = response.forms["search-form"]
        webtest_form["search_term"] = pupil_1.firstname
        webtest_form["year_group"] = pupil_1.year_group.id

        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok and search results
        assert search_response.status_code == 200

        pupils = search_response.context["page_obj"].object_list
        assert pupils == [serializers_helpers.expected_pupil(pupil_1)]

        # The form should be populated with the existing search
        webtest_form = search_response.forms["search-form"]
        assert webtest_form["search_term"].value == pupil_1.firstname

    @mock.patch.object(views.PupilSearch, "paginate_by", 1)
    def test_loads_paginated_pupils_then_form_invalid_because_no_search_term_given(
        self,
    ):
        # Create a school and authorise the test client to this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some pupil data for our school
        pupil_1 = data_factories.Pupil(pupil_id=1, school=school)
        pupil_2 = data_factories.Pupil(pupil_id=2, school=school)

        # Navigate to the pupil search view
        url = UrlName.PUPIL_LIST.url()
        response = self.client.get(url)

        # Check response ok
        assert response.status_code == 200

        # Check the pupils have been paginated across two pages
        page_1 = response.context["page_obj"]
        assert page_1.object_list == [serializers_helpers.expected_pupil(pupil_1)]
        assert page_1.has_next()

        paginator = response.context["paginator"]
        assert paginator.object_list == [
            serializers_helpers.expected_pupil(pupil_1),
            serializers_helpers.expected_pupil(pupil_2),
        ]

        # Retrieve the html form and submit an empty search term
        webtest_form = response.forms["search-form"]
        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok
        assert search_response.status_code == 200

        # Form should show errors
        django_form = search_response.context["form"]
        assert "Please enter a search term!" in django_form.errors.as_text()

        # The full pupil list should still be shown
        page_1 = search_response.context["page_obj"]
        assert page_1.object_list == [serializers_helpers.expected_pupil(pupil_1)]
        assert page_1.has_next()
