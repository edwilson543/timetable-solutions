"""
Tests for the classroom create page in the data management app.
"""

# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestClassroomCreate(TestClient):
    def test_valid_create_classroom_form_creates_classroom_in_db(self):
        # Create existing db content
        school = data_factories.School()
        classroom = data_factories.Classroom(school=school)
        new_classroom_id = classroom.classroom_id + 1

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.CLASSROOM_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]
        # Suggested value for the classroom id should be one more than next highest
        assert int(form["classroom_id"].value) == new_classroom_id

        # Fill out and submit the form
        form["classroom_id"] = new_classroom_id
        form["building"] = "Maths"
        form["room_number"] = 10

        response = form.submit()

        # Check response ok and redirects
        assert response.status_code == 302
        assert response.location == UrlName.CLASSROOM_LIST.url()

        # Check a new classroom was created in the db
        classroom = models.Classroom.objects.get(
            school_id=school.school_access_key, classroom_id=new_classroom_id
        )
        assert classroom.building == "Maths"
        assert classroom.room_number == 10

    def test_creating_classroom_with_existing_classroom_id_fails(self):
        # Create a classroom whose ID will try to create a new classroom with
        school = data_factories.School()
        existing_classroom = data_factories.Classroom(school=school)

        self.authorise_client_for_school(school)
        url = UrlName.CLASSROOM_CREATE.url()
        page = self.client.get(url)
        form = page.forms["create-form"]

        # Fill the form in using an existing classroom id
        form["classroom_id"] = existing_classroom.classroom_id
        form["building"] = "test"
        form["room_number"] = existing_classroom.room_number + 1

        form_response = form.submit()

        # Check response ok
        assert form_response.status_code == 200

        django_form = form_response.context["form"]
        errors = django_form.errors.as_text()
        assert (
            f"Classroom with id: {existing_classroom.classroom_id} already exists!"
            in errors
        )

        # Check no new classroom was created
        classrooms = models.Classroom.objects.all()
        assert classrooms.count() == 1
        assert classrooms.get() == existing_classroom
