"""
Tests for updating classroom details via the ClassroomUpdate view.
"""

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers import serializers as serializers_helpers


class TestClassroomUpdate(TestClient):
    def test_access_detail_page_with_disabled_form(self):
        # Make a classroom's data to access, with an associated lesson
        lesson = data_factories.Lesson.with_n_pupils()
        classroom = lesson.classroom
        self.authorise_client_for_school(classroom.school)

        # Navigate to this classroom's detail view
        url = UrlName.CLASSROOM_UPDATE.url(classroom_id=classroom.classroom_id)
        page = self.client.get(url)

        # Check response ok and correct context
        assert page.status_code == 200

        assert page.context[
            "serialized_model_instance"
        ] == serializers_helpers.expected_classroom(classroom)

        # Check the initial form values match the classroom's
        form = page.forms["disabled-update-form"]
        assert form["building"].value == classroom.building
        assert form["room_number"].value == str(classroom.room_number)

    def test_hx_get_enables_form_then_valid_details_submitted(self):
        # Make a classroom's data to access
        classroom = data_factories.Classroom()
        self.authorise_client_for_school(classroom.school)

        # Navigate to this classroom's detail view
        url = UrlName.CLASSROOM_UPDATE.url(classroom_id=classroom.classroom_id)
        htmx_headers = {"HX-Request": "true"}
        form_partial = self.client.get(url, headers=htmx_headers)

        # Check response ok and correct context
        assert form_partial.status_code == 200

        form = form_partial.forms["update-form"]
        assert form["building"].value == classroom.building
        assert form["room_number"].value == str(classroom.room_number)

        # Fill in and post the form
        form["building"] = "Building"
        form["room_number"] = 15

        response = form.submit(name="update-submit")

        # Check response ok and classroom details updated
        assert response.status_code == 302
        assert response.location == url

        classroom.refresh_from_db()
        assert classroom.building == "Building"
        assert classroom.room_number == 15
