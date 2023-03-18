"""Tests for forms relating to the YearGroup model."""

# Standard library imports
from unittest import mock

# Third party imports
import pytest

# Local application imports
from interfaces.data_management import forms
from tests import data_factories


@mock.patch(
    "interfaces.data_management.forms.year_group.queries.get_next_year_group_id_for_school",
)
@mock.patch(
    "interfaces.data_management.forms.year_group.queries.get_year_group_for_school",
)
@pytest.mark.django_db
class TestYearGROUPCreate:
    def test_form_valid_if_year_group_id_unique_for_school(
        self, mock_get_year_group: mock.Mock, mock_get_next_year_group: mock.Mock
    ):
        mock_get_year_group.return_value = False
        school = data_factories.School()

        form = forms.YearGroupCreate(
            school_id=school.school_access_key,
            data={
                "year_group_id": 1,
                "year_group_name": "test",
            },
        )

        assert form.is_valid()

        assert form.cleaned_data["year_group_name"] == "test"

    def test_form_invalid_if_year_group_id_already_exists_for_school(
        self, mock_get_year_group: mock.Mock, mock_get_next_year_group: mock.Mock
    ):
        mock_get_next_year_group.return_value = 123456

        yg = data_factories.YearGroup()

        form = forms.YearGroupCreate(
            school_id=yg.school.school_access_key,
            data={
                "year_group_id": yg.year_group_id,
                "year_group_name": "test",
            },
        )

        assert not form.is_valid()
        errors = form.errors.as_text()

        assert f"Year group with id: {yg.year_group_id} already exists!" in errors
        assert "The next available id is: 123456" in errors
