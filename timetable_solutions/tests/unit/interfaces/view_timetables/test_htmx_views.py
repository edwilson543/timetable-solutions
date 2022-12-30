"""
Tests for the htmx views in the view_timetables app.
"""

# Django imports
from django import test
from django import urls

# Local application imports
from data import models
from constants.url_names import UrlName


class TestLessonDetailModal(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "pupils.json",
        "teachers.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    def test_get_request_to_modal_has_200_status_and_correct_context(self):
        """
        Test that submitting a GET request to the modal (opening) endpoint is as expected.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = urls.reverse(UrlName.LESSON_DETAIL.value, kwargs={"lesson_pk": 1})

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.status_code == 200
        context = response.context
        assert context["modal_is_active"]
        assert context["lesson"] == models.Lesson.get_lesson_by_pk(pk=1)
        assert context["lesson_title"] == "Year One Maths A"

    def test_get_request_to_modal_close_has_200_status_and_correct_context(self):
        """
        Test that submitting a GET request to the modal (opening) endpoint is as expected.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = urls.reverse(UrlName.CLOSE_LESSON_DETAIL.value)

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.status_code == 200
        context = response.context
        assert not context["modal_is_active"]
