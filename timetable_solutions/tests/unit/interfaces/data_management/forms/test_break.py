"""
Unit tests for forms relating to the Break model.
"""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants
from interfaces.data_management.forms import break_ as break_forms
from tests import data_factories


@pytest.mark.django_db
class TestBreakSearch:
    def test_form_valid_for_valid_break_search_term(self):
        break_ = data_factories.Break()

        form = break_forms.BreakSearch(
            school_id=break_.school.school_access_key,
            data={"break_id": break_.break_id},
        )

        form.is_valid()

    def test_form_valid_for_day_of_week_search(self):
        school = data_factories.School()

        form = break_forms.BreakSearch(
            school_id=school.school_access_key,
            data={"day_of_week": constants.Day.MONDAY.value},
        )

        assert form.is_valid()
        assert form.cleaned_data["day_of_week"] == constants.Day.MONDAY

    def test_form_valid_for_year_group_search(self):
        yg = data_factories.YearGroup()

        form = break_forms.BreakSearch(
            school_id=yg.school.school_access_key, data={"year_group": yg.pk}
        )

        assert form.is_valid()
        assert form.cleaned_data["year_group"] == yg

    def test_form_invalid_when_no_search_term_given(self):
        school = data_factories.School()

        form = break_forms.BreakSearch(school_id=school.school_access_key, data={})

        assert not form.is_valid()
        assert "Please enter a search term!" in form.errors.as_text()
