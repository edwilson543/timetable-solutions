"""Tests for the form base classes used in data management."""

import pytest

from interfaces.data_management.forms import base_forms


class TestSearchForm:
    @pytest.mark.parametrize("search_term", ["john", "1"])
    def test_search_term_valid(self, search_term: str | int):
        form = base_forms.SearchForm(data={"search_term": search_term})

        assert form.is_valid()
        assert form.cleaned_data["search_term"] == search_term

    def test_single_character_search_term_invalid(self):
        form = base_forms.SearchForm(data={"search_term": "a"})

        assert not form.is_valid()
        assert (
            "Non-numeric search terms must be for more than one character!"
            in form.errors.as_text()
        )
