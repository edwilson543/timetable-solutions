"""
Tests for creating a new lesson.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestLessonCreate(TestClient):
    def test_valid_create_lesson_form_creates_lesson_in_db(self):
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)
        yg = data_factories.YearGroup(school=school)

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.LESSON_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]

        # Fill out and submit the form
        form["lesson_id"] = "my-lesson"
        form["subject_name"] = "Maths"
        form["teacher"] = teacher.id
        form["classroom"] = classroom.id
        form["year_group"] = yg.id
        form["total_required_slots"] = 3
        form["total_required_double_periods"] = 1

        response = form.submit()

        # Check response ok and redirects
        assert response.status_code == 302
        assert response.location == UrlName.LESSON_LIST.url()

        # Check a new lesson_ was created in the db
        lesson_ = models.Lesson.objects.get()
        assert lesson_.lesson_id == "my-lesson"
        assert lesson_.subject_name == "Maths"
        assert lesson_.teacher == teacher
        assert lesson_.classroom == classroom
        assert lesson_.total_required_slots == 3

    def test_creating_lesson_with_invalid_requirements_fails(self):
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.LESSON_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]

        # Fill out and submit the form
        form["lesson_id"] = "my-lesson"
        form["subject_name"] = "Maths"
        form["year_group"] = yg.id
        form["total_required_slots"] = 3
        form["total_required_double_periods"] = 100

        form_response = form.submit()

        # Check response ok
        assert form_response.status_code == 200

        django_form = form_response.context["form"]
        assert django_form.errors.as_text()

        # Check no lesson was created
        assert models.Lesson.objects.count() == 0
