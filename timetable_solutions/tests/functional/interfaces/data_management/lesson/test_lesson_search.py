"""
Tests for the lesson search view in the data management app.
"""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestLessonSearch(TestClient):
    def test_loads_all_lessons_for_school_then_filters_by_search_term(self):
        # Create a school and authorise the test client for this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some lessons for the school
        yg = data_factories.YearGroup(school=school)
        lesson_a = data_factories.Lesson(school=school, year_group=yg)
        data_factories.Lesson(school=school, year_group=yg)

        # Create a lesson_ at some other school
        data_factories.Lesson()

        # Navigate to the lesson_ search view
        url = UrlName.LESSON_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200
        assert len(response.context["page_obj"].object_list) == 2

        django_form = response.context["form"]
        assert not django_form.errors

        # Retrieve the html form and submit a valid search term
        webtest_form = response.forms["search-form"]
        webtest_form["search_term"] = lesson_a.lesson_id

        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok and search results
        assert search_response.status_code == 200

        lessons = search_response.context["page_obj"].object_list
        assert [lesson["lesson_id"] for lesson in lessons] == [lesson_a.lesson_id]

        # The form should be populated with the existing search
        webtest_form = search_response.forms["search-form"]
        assert webtest_form["search_term"].value == lesson_a.lesson_id

    def test_loads_paginated_lessons_then_form_invalid_because_no_search_term(self):
        # Create a school and authorise the test client to this school
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Create some lessons for the school
        yg = data_factories.YearGroup(school=school)
        data_factories.Lesson(school=school, year_group=yg)
        data_factories.Lesson(school=school, year_group=yg)

        # Navigate to the lesson_ search view
        url = UrlName.LESSON_LIST.url()
        response = self.client.get(url)

        # Check response ok and has the correct context
        assert response.status_code == 200
        assert len(response.context["page_obj"].object_list) == 2

        # Retrieve the html form and submit an empty search term
        webtest_form = response.forms["search-form"]
        search_response = webtest_form.submit(name="search-submit", value="Search")

        # Check response ok
        assert search_response.status_code == 200

        # Form should show errors
        django_form = search_response.context["form"]
        assert django_form.errors.as_text()

        # The full lesson list should still be shown
        assert len(search_response.context["page_obj"].object_list) == 2
