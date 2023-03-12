"""
Tests for the page allowing users to delete individual classrooms.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestClassroomDelete(TestClient):
    def test_successfully_deletes_classroom(self):
        classroom = data_factories.Classroom()
        self.authorise_client_for_school(classroom.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.CLASSROOM_UPDATE.url(classroom_id=classroom.classroom_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok and classroom was deleted
        assert delete_response.status_code == 302
        assert delete_response.location == UrlName.CLASSROOM_LIST.url()

        assert not models.Classroom.objects.exists()

    def test_cannot_delete_classroom_with_lessons(self):
        lesson = data_factories.Lesson.with_n_pupils(n_pupils=1)
        self.authorise_client_for_school(lesson.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.CLASSROOM_UPDATE.url(classroom_id=lesson.classroom.classroom_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok
        assert delete_response.status_code == 200

        # Check classroom was not deleted and error message shown
        assert models.Classroom.objects.count() == 1
        assert models.Classroom.objects.get() == lesson.classroom

        assert delete_response.context["deletion_error_message"]
