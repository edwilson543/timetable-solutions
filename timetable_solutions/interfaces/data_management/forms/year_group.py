"""Forms relating to the YearGroup model."""

# Django imports
from django import forms as django_forms

# Local application imports
from domain.data_management.year_groups import queries

from . import base_forms


class _YearGroupCreateUpdateBase(base_forms.CreateUpdate):
    """Base form for the year group create and update forms."""

    year_group_name = django_forms.CharField(
        required=True,
        label="Year group name",
    )


class YearGroupUpdate(_YearGroupCreateUpdateBase):
    """Form to update a year group with."""

    pass


class YearGroupCreate(YearGroupUpdate):
    year_group_id = django_forms.IntegerField(
        min_value=1,
        required=False,
        label="Year group ID",
        help_text="Unique identifier to be used for this year group. "
        "If unspecified we will use the next ID available.",
    )

    field_order = ["year_group_id", "year_group_name"]

    def clean_year_group_id(self) -> int:
        """Check the given year group id does not already exist for the school."""
        year_group_id = self.cleaned_data.get("year_group_id")
        if queries.get_year_group_for_school(
            school_id=self.school_id, year_group_id=year_group_id
        ):
            next_available_id = queries.get_next_year_group_id_for_school(
                school_id=self.school_id
            )
            raise django_forms.ValidationError(
                f"Year group with id: {year_group_id} already exists! "
                f"The next available id is: {next_available_id}"
            )
        return year_group_id
