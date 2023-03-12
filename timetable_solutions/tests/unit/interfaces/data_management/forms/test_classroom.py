"""
Tests for the classroom model forms.
"""

# Standard library imports
from unittest import mock

# Third party imports
import pytest

# Local application imports
from data import models
from interfaces.data_management import forms
from tests import data_factories


@mock.patch("interfaces.data_management.forms.classroom.queries.get_classrooms")
@pytest.mark.django_db
class TestClassroomSearch:
    def test_init_sets_building_room_number_choices(
        self, mock_get_classrooms: mock.Mock()
    ):
        # Mock the query used to retrieve all classrooms
        school = data_factories.School()
        data_factories.Classroom(school=school, building="maths", room_number=1)
        data_factories.Classroom(school=school, building="science", room_number=2)
        mock_get_classrooms.return_value = models.Classroom.objects.all()

        # Instantiate a form, which sets the building / room number choices
        form = forms.ClassroomSearch(school_id=school.school_access_key)

        # Check the choices were set as expected
        assert form.base_fields["building"].choices == [
            ("", ""),
            ("maths", "maths"),
            ("science", "science"),
        ]
        assert form.base_fields["room_number"].choices == [("", ""), (1, 1), (2, 2)]

    def test_form_with_no_search_term_not_valid(self, mock_get_classrooms: mock.Mock()):
        school = data_factories.School()
        form = forms.ClassroomSearch(school_id=school.school_access_key, data={})

        assert not form.is_valid()

        assert "You must provide at least one search term!" in form.errors.as_text()
