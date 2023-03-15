# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestPupilCreate(TestClient):
    def test_valid_create_pupil_form_creates_pupil_in_db(self):
        # Create existing db content
        school = data_factories.School()
        pupil = data_factories.Pupil(school=school)
        new_pupil_id = pupil.pupil_id + 1

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.PUPIL_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]
        # Suggested value for the pupil id should be one more than next highest
        assert int(form["pupil_id"].value) == new_pupil_id

        # Fill out and submit the form
        form["pupil_id"] = new_pupil_id
        form["firstname"] = "Dave"
        form["surname"] = "Smith"
        form["year_group"] = pupil.year_group.id

        response = form.submit()

        # Check response ok and redirects
        assert response.status_code == 302
        assert response.location == UrlName.PUPIL_LIST.url()

        # Check a new pupil was created in the db
        db_pupil = models.Pupil.objects.get(
            school_id=school.school_access_key, pupil_id=new_pupil_id
        )
        assert db_pupil.firstname == "Dave"
        assert db_pupil.surname == "Smith"
        assert db_pupil.year_group == pupil.year_group

    def test_creating_pupil_with_existing_pupil_id_fails(self):
        # Create a pupil whose ID will try to create a new pupil with
        school = data_factories.School()
        existing_pupil = data_factories.Pupil(school=school, firstname="Dave")

        self.authorise_client_for_school(school)
        url = UrlName.PUPIL_CREATE.url()
        page = self.client.get(url)
        form = page.forms["create-form"]

        # Fill the form in using an existing pupil id
        form["pupil_id"] = existing_pupil.pupil_id
        form["firstname"] = "test"
        form["surname"] = "test"
        form["year_group"] = existing_pupil.year_group.id

        form_response = form.submit()

        # Check response ok
        assert form_response.status_code == 200

        django_form = form_response.context["form"]
        errors = django_form.errors.as_text()
        assert f"Pupil with id: {existing_pupil.pupil_id} already exists!" in errors

        # Check no new pupil was created
        pupils = models.Pupil.objects.all()
        assert pupils.count() == 1
        assert pupils.get() == existing_pupil
