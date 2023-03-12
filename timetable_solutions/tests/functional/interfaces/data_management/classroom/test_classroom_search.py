"""
Tests for the classroom search view in the data management app.
"""

# Standard library imports
from unittest import mock

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import views
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestClassroomSearchList(TestClient):
    def test_loads_all_classrooms_for_school_then_filters_by_search_term(self):
        # Create a school and authorise the test client for this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some classroom data for the school
        classroom_1 = data_factories.Classroom(classroom_id=1, school=school)
        classroom_2 = data_factories.Classroom(classroom_id=2, school=school)

        # Create a classroom at some other school
        data_factories.Classroom()

        # Navigate to the classroom search view
        url = UrlName.CLASSROOM_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            serializers_helpers.expected_classroom(classroom_1),
            serializers_helpers.expected_classroom(classroom_2),
        ]

        django_form = response.context["form"]
        assert not django_form.errors

        # Retrieve the html form and submit a valid search term
        webtest_form = response.forms["search-form"]
        webtest_form["classroom_id"] = classroom_1.classroom_id
        webtest_form["building"] = classroom_1.building
        webtest_form["room_number"] = classroom_1.room_number

        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok and search results
        assert search_response.status_code == 200

        classrooms = search_response.context["page_obj"].object_list
        assert classrooms == [serializers_helpers.expected_classroom(classroom_1)]

        # The form should be populated with the existing search
        webtest_form = search_response.forms["search-form"]
        assert webtest_form["classroom_id"].value == str(classroom_1.classroom_id)
        assert webtest_form["building"].value == classroom_1.building
        assert webtest_form["room_number"].value == str(classroom_1.room_number)

    @mock.patch.object(views.ClassroomSearch, "paginate_by", 1)
    def test_loads_paginated_classrooms_then_form_invalid_because_no_search_term_given(
        self,
    ):
        # Create a school and authorise the test client to this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some classroom data for our school
        classroom_1 = data_factories.Classroom(classroom_id=1, school=school)
        classroom_2 = data_factories.Classroom(classroom_id=2, school=school)

        # Navigate to the classroom search view
        url = UrlName.CLASSROOM_LIST.url()
        response = self.client.get(url)

        # Check response ok
        assert response.status_code == 200

        # Check the classrooms have been paginated across two pages
        page_1 = response.context["page_obj"]
        assert page_1.object_list == [
            serializers_helpers.expected_classroom(classroom_1)
        ]
        assert page_1.has_next()

        paginator = response.context["paginator"]
        assert paginator.object_list == [
            serializers_helpers.expected_classroom(classroom_1),
            serializers_helpers.expected_classroom(classroom_2),
        ]

        # Retrieve the html form and submit an empty search term
        webtest_form = response.forms["search-form"]
        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok
        assert search_response.status_code == 200

        # Form should show errors
        django_form = search_response.context["form"]
        assert "Please enter a search term!" in django_form.errors.as_text()

        # The full classroom list should still be shown
        page_1 = search_response.context["page_obj"]
        assert page_1.object_list == [
            serializers_helpers.expected_classroom(classroom_1)
        ]
        assert page_1.has_next()
