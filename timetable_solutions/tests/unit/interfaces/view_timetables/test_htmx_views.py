"""
Tests for the htmx views in the view_timetables app.
"""


# Django imports
from django import test, urls

# Local application imports
from data import models
from interfaces.constants import UrlName


class TestLessonDetailModal(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "teachers.json",
        "classrooms.json",
        "year_groups.json",
        "pupils.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    def test_get_request_to_modal_has_200_status_and_correct_context(self):
        """
        Test that submitting a GET request to the modal (opening) endpoint is as expected.
        """
        # Set test parameters
        self.client.login(username="dummy_teacher", password="dt123dt123")
        url = urls.reverse(
            UrlName.LESSON_DETAIL.value, kwargs={"lesson_id": "YEAR_ONE_MATHS_A"}
        )

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.status_code == 200
        context = response.context
        assert context["modal_is_active"]
        assert context["lesson"] == models.Lesson.objects.get_individual_lesson(
            school_id=123456, lesson_id="YEAR_ONE_MATHS_A"
        )
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
