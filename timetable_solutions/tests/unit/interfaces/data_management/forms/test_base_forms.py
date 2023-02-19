"""Tests for the form base classes used in data management."""

import pytest

from interfaces.data_management.forms import base_forms


class TestSearch:
    @pytest.mark.parametrize("search_term", ["john", "1"])
    def test_search_term_valid(self, search_term: str | int):
        form = base_forms.Search(data={"search_term": search_term})

        assert form.is_valid()
        assert form.cleaned_data["search_term"] == search_term

    def test_no_search_term_invalid(self):
        form = base_forms.Search(data={})

        assert not form.is_valid()
        assert "Please enter a search term!" in form.errors.as_text()

    def test_single_character_search_term_invalid(self):
        form = base_forms.Search(data={"search_term": "a"})

        assert not form.is_valid()
        assert (
            "Non-numeric search terms must be more than one character!"
            in form.errors.as_text()
        )


class TestCreateUpdate:
    def test_school_id_set_as_instance_attribute(self):
        form = base_forms.CreateUpdate(school_id=1)

        assert form.school_id == 1
