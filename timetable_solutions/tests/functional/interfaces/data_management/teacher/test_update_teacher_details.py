"""Tests for the TeacherUpdate view."""

from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestTeacherUpdate(TestClient):
    def test_access_detail_page_with_disabled_form(self):
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

    def test_hx_get_enables_form_then_valid_details_submitted(self):
        # Make a teacher's data to access
        teacher = data_factories.Teacher()
        self.authorise_client_for_school(teacher.school)

        # Navigate to this teacher's detail view
        url = UrlName.TEACHER_UPDATE.url(teacher_id=teacher.teacher_id)
        htmx_headers = {"HTTP_HX-Request": "true"}
        form_partial = self.client.get(url, headers=htmx_headers)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["add-update-form"]
        assert form["firstname"].value == teacher.firstname
        assert form["surname"].value == teacher.surname
        assert form["title"].value == teacher.title

        # Fill in and post the form
        form["firstname"] = "Ed"
        form["surname"] = "Wilson"
        form["title"] = "Mr"

        response = form.submit()

        # Check response ok and teacher details updated
        assert response.status_code == 302
        assert response.location == url

        db_teacher = models.Teacher.objects.get(
            school_id=teacher.school.school_access_key, teacher_id=teacher.teacher_id
        )

        assert db_teacher.firstname == "Ed"
        assert db_teacher.surname == "Wilson"
        assert db_teacher.title == "Mr"
