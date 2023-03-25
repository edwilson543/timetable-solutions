"""Tests for updating teacher details via the TeacherUpdate view."""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestTeacherUpdate(TestClient):
    def test_access_detail_page_with_disabled_form(self):
        # Make a teacher's data to access, with an associated lesson
        lesson = data_factories.Lesson.with_n_pupils()
        teacher = lesson.teacher
        self.authorise_client_for_school(teacher.school)

        # Navigate to this teacher's detail view
        url = UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        assert page.context[
            "serialized_model_instance"
        ] == serializers_helpers.expected_teacher(teacher)

        # Check the initial form values match the teacher's
        form = page.forms["disabled-update-form"]
        assert form["firstname"].value == teacher.firstname
        assert form["surname"].value == teacher.surname
        assert form["title"].value == teacher.title

    def test_hx_get_enables_form_then_valid_details_submitted(self):
        # Make a teacher's data to access
        teacher = data_factories.Teacher()
        self.authorise_client_for_school(teacher.school)

        # Navigate to this teacher's detail view
        url = UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id)
        htmx_headers = {"HX-Request": "true"}
        form_partial = self.client.get(url, headers=htmx_headers)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]
        assert form["firstname"].value == teacher.firstname
        assert form["surname"].value == teacher.surname
        assert form["title"].value == teacher.title

        # Fill in and post the form
        form["firstname"] = "Ed"
        form["surname"] = "Wilson"
        form["title"] = "Mr"

        response = form.submit(name="update-submit")

        # Check response ok and teacher details updated
        assert response.status_code == 302
        assert response.location == url

        teacher.refresh_from_db()
        assert teacher.firstname == "Ed"
        assert teacher.surname == "Wilson"
        assert teacher.title == "Mr"
