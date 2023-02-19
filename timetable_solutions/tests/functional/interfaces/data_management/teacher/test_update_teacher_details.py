"""Tests for the TeacherUpdate view."""

from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestTeacherUpdate(TestClient):
    def test_access_detail_page_then_change_teachers_detail(self):
        # Make a teacher's data to access
        teacher = data_factories.Teacher()
        self.authorise_client_for_school(teacher.school)

        # Navigate to this teacher's detail view
        url = UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        assert page.context["model_instance"] == teacher

        form = page.forms["disabled-change-form"]
        assert form["firstname"].value == teacher.firstname
        assert form["surname"].value == teacher.surname
        assert form["title"].value == teacher.title

        # Enable the form for editing
        edit_response = form.submit()

        # TODO -> submit the new editable form
