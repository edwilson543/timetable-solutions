"""
Tests for forms relating to the Pupil model.
"""

# Standard library imports
from unittest import mock

# Third party imports
import pytest

# Local application imports
from interfaces.data_management.forms import pupil as pupil_forms
from tests import data_factories


@pytest.mark.django_db
class TestPupilSearch:
    def test_form_valid_for_just_year_group(self):
        school = data_factories.School()
        yg_a = data_factories.YearGroup(school=school, year_group_name="aaa")
        yg_b = data_factories.YearGroup(school=school, year_group_name="bbb")
        data_factories.YearGroup()

        form = pupil_forms.PupilSearch(
            school_id=school.school_access_key, data={"year_group": yg_a.pk}
        )

        # Check form valid and yg normalised to a model instance
        assert form.is_valid()
        assert form.cleaned_data["year_group"] == yg_a

        # Check the year group queryset had been correctly set
        queryset = form.base_fields["year_group"].queryset
        assert queryset.count() == 2
        assert queryset.first() == yg_a
        assert yg_b in queryset

    def test_form_valid_for_just_search_term(self):
        school = data_factories.School()

        form = pupil_forms.PupilSearch(
            school_id=school.school_access_key, data={"search_term": "Dave"}
        )

        assert form.is_valid()

    def test_form_invalid_for_no_search_term(self):
        school = data_factories.School()

        form = pupil_forms.PupilSearch(school_id=school.school_access_key, data={})

        assert not form.is_valid()


@pytest.mark.django_db
class TestPupilCreateUpdateBase:
    def test_form_valid_for_valid_pupil(self):
        yg = data_factories.YearGroup()

        form = pupil_forms._PupilCreateUpdateBase(
            school_id=yg.school.school_access_key,
            data={"firstname": "Ed", "surname": "Wilson", "year_group": yg.pk},
        )

        assert form.is_valid()


@mock.patch(
    "interfaces.data_management.forms.pupil.queries.get_next_pupil_id_for_school",
)
@mock.patch(
    "interfaces.data_management.forms.pupil.queries.get_pupils",
)
@pytest.mark.django_db
class TestPupilCreate:
    def test_form_invalid_if_pupil_id_already_exists_for_school(
        self, mock_get_pupils: mock.Mock(), mock_get_next_pupil_id: mock.Mock()
    ):
        pupil = data_factories.Pupil()

        mock_get_next_pupil_id.return_value = 123456
        mock_get_pupils.return_value = pupil

        form = pupil_forms.PupilCreate(
            school_id=pupil.school.school_access_key,
            data={
                "pupil_id": pupil.pupil_id,
                "firstname": "test-firstname",
                "surname": "test-surname",
                "year_group": pupil.year_group,
            },
        )

        assert not form.is_valid()
        errors = form.errors.as_text()

        assert f"Pupil with id: {pupil.pupil_id} already exists!" in errors
        assert f"The next available id is: 123456" in errors
