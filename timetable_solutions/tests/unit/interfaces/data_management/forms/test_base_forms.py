import pytest

from interfaces.data_management.forms import base_forms


class TestSearchForm:
    @pytest.mark.parametrize("search_term", ["john", "1"])
    def test_search_term_valid(self, search_term: str | int):
        form = base_forms.SearchForm(data={"search_term": search_term})

        assert form.is_valid()
        assert form.cleaned_data["search_term"] == search_term
