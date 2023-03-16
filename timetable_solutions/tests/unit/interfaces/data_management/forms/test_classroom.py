"""
Tests for the classroom model forms.
"""

# Standard library imports
from unittest import mock

# Third party imports
import pytest

# Local application imports
from data import models
from interfaces.data_management.forms import classroom as classroom_forms
from tests import data_factories


@mock.patch("interfaces.data_management.forms.classroom.queries.get_classrooms")
@pytest.mark.django_db
class TestClassroomSearch:
    def test_init_sets_building_room_number_choices(
        self, mock_get_classrooms: mock.Mock
    ):
        # Mock the query used to retrieve all classrooms
        school = data_factories.School()
        data_factories.Classroom(school=school, building="maths", room_number=1)
        data_factories.Classroom(school=school, building="science", room_number=2)
        mock_get_classrooms.return_value = models.Classroom.objects.all()

        # Instantiate a form, which sets the building / room number choices
        form = classroom_forms.ClassroomSearch(school_id=school.school_access_key)

        # Check the choices were set as expected
        assert form.base_fields["building"].choices == [
            ("", ""),
            ("maths", "maths"),
            ("science", "science"),
        ]
        assert form.base_fields["room_number"].choices == [("", ""), (1, 1), (2, 2)]

    def test_form_with_no_search_term_not_valid(self, mock_get_classrooms: mock.Mock):
        school = data_factories.School()
        form = classroom_forms.ClassroomSearch(
            school_id=school.school_access_key, data={}
        )

        assert not form.is_valid()

        assert "Please enter a search term!" in form.errors.as_text()


@mock.patch("interfaces.data_management.forms.classroom.queries.get_classrooms")
@pytest.mark.django_db
class TestClassroomCreateUpdateBase:
    def test_form_valid_for_valid_classroom(self, mock_get_classrooms: mock.Mock):
        mock_get_classrooms.return_value = models.ClassroomQuerySet().none()
        school = data_factories.School()

        form = classroom_forms._ClassroomCreateUpdateBase(
            school_id=school.school_access_key,
            data={"building": "maths", "room_number": 10},
        )

        assert form.is_valid()

    def test_form_invalid_for_non_unique_building_room_number_combination(
        self, mock_get_classrooms: mock.Mock
    ):
        classroom = data_factories.Classroom()
        mock_get_classrooms.return_value = models.Classroom.objects.all()

        form = classroom_forms._ClassroomCreateUpdateBase(
            school_id=classroom.school.school_access_key,
            data={"building": classroom.building, "room_number": classroom.room_number},
        )

        assert not form.is_valid()

        assert (
            "Classroom in this building with this room number already exists!"
            in form.errors.as_text()
        )


@mock.patch("interfaces.data_management.forms.classroom.queries.get_classrooms")
@pytest.mark.django_db
class TestClassroomCreate:
    def test_form_valid_for_valid_classroom(self, mock_get_classrooms: mock.Mock):
        mock_get_classrooms.return_value = models.ClassroomQuerySet().none()
        school = data_factories.School()

        form = classroom_forms.ClassroomCreate(
            school_id=school.school_access_key,
            data={"classroom_id": 1, "building": "maths", "room_number": 10},
        )

        assert form.is_valid()

    def test_form_invalid_for_non_unique_classroom_id(
        self, mock_get_classrooms: mock.Mock
    ):
        classroom = data_factories.Classroom(building="science", room_number=100)
        mock_get_classrooms.return_value = models.Classroom.objects.all()

        form = classroom_forms.ClassroomCreate(
            school_id=classroom.school.school_access_key,
            data={
                "classroom_id": classroom.classroom_id,
                "building": "maths",
                "room_number": 10,
            },
        )

        assert not form.is_valid()

        assert (
            f"Classroom with id: {classroom.classroom_id} already exists!"
            in form.errors.as_text()
        )
