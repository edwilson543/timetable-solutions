"""Tests for updating pupil details via the PupilUpdate view."""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestPupilUpdate(TestClient):
    def test_access_detail_page_with_disabled_form(self):
        # Make a pupil's data to access, with an associated lesson
        lesson = data_factories.Lesson.with_n_pupils()
        pupil = lesson.pupils.first()
        self.authorise_client_for_school(pupil.school)

        # Navigate to this pupil's detail view
        url = UrlName.PUPIL_UPDATE.url(pupil_id=pupil.pupil_id)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        assert page.context[
            "serialized_model_instance"
        ] == serializers_helpers.expected_pupil(pupil)

        # Check the initial form values match the pupil's
        form = page.forms["disabled-update-form"]
        assert form["firstname"].value == pupil.firstname
        assert form["surname"].value == pupil.surname
        assert form["year_group"].value == str(pupil.year_group.id)

    def test_hx_get_enables_form_then_valid_details_submitted(self):
        # Make a pupil's data to access
        pupil = data_factories.Pupil()
        other_yg = data_factories.YearGroup(school=pupil.school)
        self.authorise_client_for_school(pupil.school)

        # Navigate to this pupil's detail view
        url = UrlName.PUPIL_UPDATE.url(pupil_id=pupil.pupil_id)
        htmx_headers = {"HTTP_HX-Request": "true"}
        form_partial = self.client.get(url, headers=htmx_headers)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]
        assert form["firstname"].value == pupil.firstname
        assert form["surname"].value == pupil.surname
        assert form["year_group"].value == str(pupil.year_group.id)

        # Fill in and post the form
        form["firstname"] = "Ed"
        form["surname"] = "Wilson"
        form["year_group"] = other_yg.id

        response = form.submit(name="update-submit")

        # Check response ok and pupil details updated
        assert response.status_code == 302
        assert response.location == url

        pupil.refresh_from_db()
        assert pupil.firstname == "Ed"
        assert pupil.surname == "Wilson"
        assert pupil.year_group == other_yg
