"""Tests for the teacher search view in the data management app."""

# Standard library imports
from unittest import mock

# Local application imports
from interfaces.constants import UrlName
from interfaces.data_management import views
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestTeacherSearchList(TestClient):
    def test_loads_all_teachers_for_school_then_filters_by_search_term(self):
        # Create a school and authorise the test client for this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some teacher data for the school
        teacher_1 = data_factories.Teacher(teacher_id=1, school=school)
        teacher_2 = data_factories.Teacher(teacher_id=2, school=school)

        # Create a teacher at some other school
        data_factories.Teacher()

        # Navigate to the teacher search view
        url = UrlName.TEACHER_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200
        assert response.context["page_obj"].object_list == [
            serializers_helpers.expected_teacher(teacher_1),
            serializers_helpers.expected_teacher(teacher_2),
        ]

        django_form = response.context["form"]
        assert not django_form.errors

        # Retrieve the html form and submit a valid search term
        webtest_form = response.forms["search-form"]
        webtest_form["search_term"] = teacher_1.firstname

        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok and search results
        assert search_response.status_code == 200

        teachers = search_response.context["page_obj"].object_list
        assert teachers == [serializers_helpers.expected_teacher(teacher_1)]

        # The form should be populated with the existing search
        webtest_form = search_response.forms["search-form"]
        assert webtest_form["search_term"].value == teacher_1.firstname

    @mock.patch.object(views.TeacherSearch, "paginate_by", 1)
    def test_loads_paginated_teachers_then_form_invalid_because_no_search_term_given(
        self,
    ):
        # Create a school and authorise the test client to this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some teacher data for our school
        teacher_1 = data_factories.Teacher(teacher_id=1, school=school)
        teacher_2 = data_factories.Teacher(teacher_id=2, school=school)

        # Navigate to the teacher search view
        url = UrlName.TEACHER_LIST.url()
        response = self.client.get(url)

        # Check response ok
        assert response.status_code == 200

        # Check the teachers have been paginated across two pages
        page_1 = response.context["page_obj"]
        assert page_1.object_list == [serializers_helpers.expected_teacher(teacher_1)]
        assert page_1.has_next()

        paginator = response.context["paginator"]
        assert paginator.object_list == [
            serializers_helpers.expected_teacher(teacher_1),
            serializers_helpers.expected_teacher(teacher_2),
        ]

        # Retrieve the html form and submit an empty search term
        webtest_form = response.forms["search-form"]
        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok
        assert search_response.status_code == 200

        # Form should show errors
        django_form = search_response.context["form"]
        assert "Please enter a search term!" in django_form.errors.as_text()

        # The full teacher list should still be shown
        page_1 = search_response.context["page_obj"]
        assert page_1.object_list == [serializers_helpers.expected_teacher(teacher_1)]
        assert page_1.has_next()
