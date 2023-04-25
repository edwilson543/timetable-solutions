"""
Tests for the page allowing users to delete individual lessons.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestLessonDelete(TestClient):
    def test_successfully_deletes_lesson(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        lesson = data_factories.Lesson(school=school, year_group=yg)
        self.authorise_client_for_school(lesson.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.LESSON_UPDATE.url(lesson_id=lesson.lesson_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok and lesson_ was deleted
        assert delete_response.status_code == 302
        assert delete_response.location == UrlName.LESSON_LIST.url()

        assert not models.Lesson.objects.exists()
