# Local application imports
from data import models
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestYearGroupCreate(TestClient):
    def test_valid_create_year_group_form_creates_year_group_in_db(self):
        # Create existing db content
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        new_yg_id = yg.year_group_id + 1

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.YEAR_GROUP_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]
        # Suggested value for the year group id should be one more than next highest
        assert int(form["year_group_id"].value) == new_yg_id

        # Fill out and submit the form
        form["year_group_id"] = new_yg_id
        form["year_group_name"] = "Test"

        response = form.submit()

        # Check response ok and redirects
        assert response.status_code == 302
        assert response.location == UrlName.YEAR_GROUP_UPDATE.url(
            year_group_id=new_yg_id
        )

        # Check a new year group was created in the db
        yg = models.YearGroup.objects.get(
            school_id=school.school_access_key, year_group_id=new_yg_id
        )
        assert yg.year_group_name == "Test"

    def test_creating_year_group_with_existing_year_group_id_fails(self):
        # Create a year group whose ID we will try to create a new year group with
        school = data_factories.School()
        existing_yg = data_factories.YearGroup(school=school)

        # Authorise the client to this school and navigate to add page
        self.authorise_client_for_school(school)
        url = UrlName.YEAR_GROUP_CREATE.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        form = page.forms["create-form"]

        # Fill out and submit the form, with the id as that of the existing year group
        form["year_group_id"] = existing_yg.year_group_id
        form["year_group_name"] = "Test"

        form_response = form.submit()

        # Check response ok
        assert form_response.status_code == 200

        django_form = form_response.context["form"]
        errors = django_form.errors.as_text()
        assert (
            f"Year group with id: {existing_yg.year_group_id} already exists!" in errors
        )

        # Check no new year group was created
        ygs = models.YearGroup.objects.all()
        assert ygs.get() == existing_yg
