"""Tests for the page allowing users to delete individual teachers."""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestTeacherDelete(TestClient):
    def test_successfully_deletes_teacher(self):
        teacher = data_factories.Teacher()
        self.authorise_client_for_school(teacher.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok and teacher was deleted
        assert delete_response.status_code == 302
        assert delete_response.location == UrlName.TEACHER_LIST.url()

        assert not models.Teacher.objects.exists()

    def test_cannot_delete_teacher_with_lessons(self):
        lesson = data_factories.Lesson.with_n_pupils(n_pupils=1)
        self.authorise_client_for_school(lesson.school)

        # Note the deletion form is shown on the update page, so navigate the client here
        url = UrlName.TEACHER_UPDATE.url(teacher_id=lesson.teacher.teacher_id)
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        deletion_form = page.forms["delete-form"]

        delete_response = deletion_form.submit()

        # Check response ok
        assert delete_response.status_code == 200

        # Check teacher was not deleted and error message shown
        assert models.Teacher.objects.count() == 1
        assert models.Teacher.objects.get() == lesson.teacher

        assert delete_response.context["deletion_error_message"]
