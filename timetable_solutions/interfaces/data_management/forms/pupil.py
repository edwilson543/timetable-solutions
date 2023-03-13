"""
Forms relating to the Pupil model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from data import models


class PupilSearch(django_forms.Form):
    """
    Search form for the pupil model.
    """

    search_term = django_forms.CharField(
        required=False, label="Search for a pupil by name or id"
    )
    year_group = django_forms.ModelChoiceField(
        required=False,
        label="Year group",
        empty_label="",
        queryset=models.YearGroupQuerySet().none(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Get and set the classrooms and room number choices
        """
        school_id = kwargs.pop("school_id")
        year_groups = models.YearGroup.objects.get_all_instances_for_school(
            school_id=school_id
        ).order_by("year_group_name")
        self.base_fields["year_group"].queryset = year_groups

        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        """
        Ensure some search criteria was given.
        """
        search_term = self.cleaned_data["search_term"]
        year_group = self.cleaned_data["year_group"]
        if not search_term and not year_group:
            raise django_forms.ValidationError("Please enter a search term!")

        return self.cleaned_data
