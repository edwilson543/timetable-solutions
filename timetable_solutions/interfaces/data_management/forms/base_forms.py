from typing import Any

from django import forms


class Search(forms.Form):
    """Form providing a single search field."""

    search_term = forms.CharField(
        required=True,
        label="Search term",
        initial="",
        error_messages={"required": "Please enter a search term!"},
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set any field parameters provided by constructor."""
        if kwargs.get("search_help_text"):
            self.base_fields["search_term"].help_text = kwargs.pop("search_help_text")
        super().__init__(*args, **kwargs)

    def clean_search_term(self) -> str:
        """Prevent single letter searches."""
        if search_term := self.cleaned_data.get("search_term"):
            try:
                int(search_term)
            except ValueError:
                if len(search_term) < 2:
                    raise forms.ValidationError(
                        "Non-numeric search terms must be more than one character!"
                    )
        return search_term


class CreateUpdate(forms.Form):
    """Base form for creating and updating individual models."""

    def __init__(self, *args: object, **kwargs: int) -> None:
        """
        Set the school, which may be used as context in validation.

        e.g. checking IDs are unique for a school
        """
        school_id = kwargs.pop("school_id")
        self.school_id = school_id
        super().__init__(*args, **kwargs)
