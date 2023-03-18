"""Tests for forms relating to the Teacher model."""

# Standard library imports
from unittest import mock

# Third party imports
import pytest

# Local application imports
from interfaces.data_management.forms import teacher as teacher_forms
from tests import data_factories


class TestTeacherSearch:
    @pytest.mark.parametrize("search_term", ["john", "1"])
    def test_search_term_valid(self, search_term: str | int):
        form = teacher_forms.TeacherSearch(data={"search_term": search_term})

        assert form.is_valid()
        assert form.cleaned_data["search_term"] == search_term

    def test_no_search_term_invalid(self):
        form = teacher_forms.TeacherSearch(data={})

        assert not form.is_valid()
        assert "Please enter a search term!" in form.errors.as_text()

    def test_single_character_search_term_invalid(self):
        form = teacher_forms.TeacherSearch(data={"search_term": "a"})

        assert not form.is_valid()
        assert (
            "Non-numeric search terms must be more than one character!"
            in form.errors.as_text()
        )


@mock.patch(
    "interfaces.data_management.forms.teacher.queries.get_next_teacher_id_for_school",
)
@mock.patch(
    "interfaces.data_management.forms.teacher.queries.get_teacher_for_school",
)
@pytest.mark.django_db
class TestTeacherCreateUpdateBase:
    def test_form_valid_if_teacher_id_unique_for_school(
        self, mock_get_teacher: mock.Mock, mock_get_next_teacher: mock.Mock
    ):
        mock_get_teacher.return_value = False

        school = data_factories.School()

        form = teacher_forms._TeacherCreateUpdateBase(
            school_id=school.school_access_key,
            data={
                "teacher_id": 1,
                "firstname": "test-firstname",
                "surname": "test-surname",
                "title": "test-title",
            },
        )

        assert form.is_valid()

        assert form.cleaned_data["firstname"] == "test-firstname"
        assert form.cleaned_data["surname"] == "test-surname"
        assert form.cleaned_data["title"] == "test-title"


@mock.patch(
    "interfaces.data_management.forms.teacher.queries.get_next_teacher_id_for_school",
)
@mock.patch(
    "interfaces.data_management.forms.teacher.queries.get_teacher_for_school",
)
@pytest.mark.django_db
class TestTeacherCreate:
    def test_form_invalid_if_teacher_id_already_exists_for_school(
        self, mock_get_teacher: mock.Mock, mock_get_next_teacher: mock.Mock
    ):
        teacher = data_factories.Teacher()

        mock_get_next_teacher.return_value = 123456
        mock_get_teacher.return_value = teacher

        form = teacher_forms.TeacherCreate(
            school_id=teacher.school.school_access_key,
            data={
                "teacher_id": teacher.teacher_id,
                "firstname": "test-firstname",
                "surname": "test-surname",
                "title": "test-title",
            },
        )

        assert not form.is_valid()
        errors = form.errors.as_text()

        assert f"Teacher with id: {teacher.teacher_id} already exists!" in errors
        assert "The next available id is: 123456" in errors
