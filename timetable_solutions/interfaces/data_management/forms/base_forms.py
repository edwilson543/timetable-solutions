"""Base forms that are subclassed or just used directly for managing individual models."""

# Django imports
from django import forms
from django.core.files import uploadedfile


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


class BulkUpload(forms.Form):
    """Form for uploading a file to populate a db table with."""

    csv_file = forms.FileField(required=True, label="Upload a file")

    def clean_csv_file(self) -> uploadedfile.SimpleUploadedFile:
        """Check the file has the correct extension."""
        file = self.cleaned_data["csv_file"]
        try:
            extension = file.name.split(".")[1]
            if extension != "csv":
                raise forms.ValidationError(
                    f"The given file had extension: {extension}. Please provide a .csv file!"
                )
        except IndexError:
            raise forms.ValidationError(
                "The given file had no file extension. Please provide a .csv file!"
            )
        return file
