from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestTeacherCreate(TestClient):
    def test_valid_add_teacher_form_creates_teacher_in_db(self):
        # Create existing db content
        school = data_factories.School()
        teacher = data_factories.Teacher(school=school, teacher_id=1)

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.TEACHER_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]
        # Suggested value for the teacher id should be one more than next highest
        assert int(form["teacher_id"].value) == teacher.teacher_id + 1

        # Fill out and submit the form
        form["teacher_id"] = 2
        form["firstname"] = "Dave"
        form["surname"] = "Smith"
        form["title"] = "Miss"

        response = form.submit()

        # Check response ok and redirects
        assert response.status_code == 302
        assert response.location == UrlName.TEACHER_UPDATE.url(teacher_id=2)

        # Check a new teacher was created in the db
        db_teacher = models.Teacher.objects.get(
            school_id=school.school_access_key, teacher_id=2
        )
        assert db_teacher.firstname == "Dave"
        assert db_teacher.surname == "Smith"
        assert db_teacher.title == "Miss"

    def test_creating_teacher_with_existing_teacher_id_fails(self):
        # Create a teacher whose ID will try to create a new teacher with
        school = data_factories.School()
        existing_teacher = data_factories.Teacher(school=school, firstname="Dave")

        self.authorise_client_for_school(school)
        url = UrlName.TEACHER_CREATE.url()
        page = self.client.get(url)
        form = page.forms["create-form"]

        # Fill the form in using an existing teacher id
        form["teacher_id"] = existing_teacher.teacher_id
        form["firstname"] = "test"
        form["surname"] = "test"
        form["title"] = "test"

        form_response = form.submit()

        # Check response ok
        assert form_response.status_code == 200

        django_form = form_response.context["form"]
        errors = django_form.errors.as_text()
        assert (
            f"Teacher with id: {existing_teacher.teacher_id + 1} already exists!"
            in errors
        )

        # Check no new teacher was created
        teachers = models.Teacher.objects.all()
        assert teachers.count() == 1
        assert teachers.get().firstname != "test"
