from django import forms


class SearchForm(forms.Form):
    """Form providing a single search field."""

    search_term = forms.CharField(
        required=True,
        label="Search term",
        initial="",
        error_messages={"required": "Please enter a search term!"},
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Set any parameters overriden in child classes."""
        if kwargs.get("search_help_text"):
            self.base_fields["search_term"].help_text = kwargs.pop("search_help_text")
        super().__init__(*args, **kwargs)
