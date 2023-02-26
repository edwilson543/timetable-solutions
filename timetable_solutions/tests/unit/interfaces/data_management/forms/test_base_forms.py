"""Tests for the form base classes used in data management."""

# Standard library imports
import io

# Third party imports
import pytest

# Django imports
from django.core.files import uploadedfile

# Local application imports
from interfaces.data_management.forms import base_forms
from tests.utils import get_csv_from_lists


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


class TestBulkUpload:
    @pytest.fixture
    def csv_buffer(self) -> io.BytesIO:
        return get_csv_from_lists([["header", "some_other_header"], [1, 2]])

    def test_csv_file_is_valid(self, csv_buffer: io.BytesIO):
        csv_file = uploadedfile.SimpleUploadedFile(
            name="test.csv",
            content=csv_buffer.read(),
        )

        form = base_forms.BulkUpload(files={"csv_file": csv_file})

        assert form.is_valid()

    @pytest.mark.parametrize("file_extension", [".xlsx", ""])
    def test_invalid_file_extension_rejected(
        self, file_extension: str, csv_buffer: io.BytesIO
    ):
        csv_file = uploadedfile.SimpleUploadedFile(
            name=f"test{file_extension}",
            content=csv_buffer.read(),
        )

        form = base_forms.BulkUpload(files={"csv_file": csv_file})

        assert not form.is_valid()
