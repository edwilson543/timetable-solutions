"""
Forms relating to the Pupil model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from data import models
from domain.data_management.pupils import queries


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
        Get and set the year group choices.
        """
        school_id = kwargs.pop("school_id")
        super().__init__(*args, **kwargs)

        year_groups = models.YearGroup.objects.get_all_instances_for_school(
            school_id=school_id
        ).order_by("year_group_name")
        self.fields["year_group"].queryset = year_groups

    def clean(self) -> dict[str, Any]:
        """
        Ensure some search criteria was given.
        """
        search_term = self.cleaned_data["search_term"]
        year_group = self.cleaned_data["year_group"]
        if not search_term and not year_group:
            raise django_forms.ValidationError("Please enter a search term!")

        return self.cleaned_data


class _PupilCreateUpdateBase(django_forms.Form):
    """
    Base form for the pupil create and update forms.
    """

    firstname = django_forms.CharField(required=True, label="Firstname")

    surname = django_forms.CharField(required=True, label="Surname")

    year_group = django_forms.ModelChoiceField(
        required=True,
        label="Year group",
        empty_label="",
        queryset=models.YearGroupQuerySet().none(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Get and set the year group choices.
        """
        self.school_id = kwargs.pop("school_id")
        super().__init__(*args, **kwargs)

        year_groups = models.YearGroup.objects.get_all_instances_for_school(
            school_id=self.school_id
        ).order_by("year_group_name")
        self.fields["year_group"].queryset = year_groups


class PupilUpdate(_PupilCreateUpdateBase):
    """
    Form for updating pupils with.
    """

    pass


class PupilCreate(_PupilCreateUpdateBase):
    """
    Form for creating pupils with.
    """

    pupil_id = django_forms.IntegerField(
        min_value=1,
        required=False,
        label="Pupil ID",
        help_text="Unique identifier to be used for this pupil. "
        "If unspecified we will use the next ID available.",
    )

    field_order = ["pupil_id", "firstname", "surname", "year_group"]

    def clean_pupil_id(self) -> int:
        """
        Check the given pupil id does not already exist for the school.
        """
        pupil_id = self.cleaned_data.get("pupil_id")
        if queries.get_pupils(school_id=self.school_id, search_term=pupil_id):
            next_available_id = queries.get_next_pupil_id_for_school(
                school_id=self.school_id
            )
            raise django_forms.ValidationError(
                f"Pupil with id: {pupil_id} already exists! "
                f"The next available id is: {next_available_id}"
            )
        return pupil_id
