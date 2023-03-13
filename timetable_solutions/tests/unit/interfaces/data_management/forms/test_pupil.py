"""
Tests for forms relating to the Pupil model.
"""

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
