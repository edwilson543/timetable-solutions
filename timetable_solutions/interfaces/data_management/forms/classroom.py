"""
Forms relating to the Teacher model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from domain.data_management.classrooms import queries
from interfaces.data_management.forms import base_forms


class ClassroomSearch(django_forms.Form):
    """
    Search form for the classroom model.
    """

    classroom_id = django_forms.IntegerField(required=False, label="Classroom ID")
    building = django_forms.ChoiceField(required=False, label="Building")
    room_number = django_forms.TypedChoiceField(
        required=False, label="Room number", coerce=int, empty_value=""
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Get and set the classrooms and room number choices
        """
        school_id = kwargs.pop("school_id")
        classrooms = queries.get_classrooms(school_id=school_id).values(
            "building", "room_number"
        )
        buildings = [("", "")] + sorted(
            {(classroom["building"], classroom["building"]) for classroom in classrooms}
        )
        room_numbers = [("", "")] + sorted(
            {
                (classroom["room_number"], classroom["room_number"])
                for classroom in classrooms
            }
        )
        self.base_fields["building"].choices = buildings
        self.base_fields["room_number"].choices = room_numbers
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        classroom_id = self.cleaned_data.get("classroom_id")
        building = self.cleaned_data.get("building")
        room_number = self.cleaned_data.get("room_number")
        if not building and not room_number and not classroom_id:
            raise django_forms.ValidationError(
                "You must provide at least one search term!"
            )
        return self.cleaned_data


class _ClassroomCreateUpdateBase(base_forms.CreateUpdate):
    """
    Base form for the classroom create and update forms.
    """

    building = django_forms.CharField(
        required=True,
        label="Building",
    )

    room_number = django_forms.IntegerField(
        required=True,
        label="Room number",
    )

    def clean(self) -> dict[str, Any]:
        """
        Ensure the building / room number combination is unique to the school.
        """
        building = self.cleaned_data["building"]
        room_number = self.cleaned_data["room_number"]
        if queries.get_classrooms(
            school_id=self.school_id, building=building.lower(), room_number=room_number
        ).exists():
            raise django_forms.ValidationError(
                "Classroom in this building with this room number already exists!"
            )
        return self.cleaned_data


class ClassroomUpdate(_ClassroomCreateUpdateBase):
    """
    Form to update a classroom with.
    """

    pass


class ClassroomCreate(_ClassroomCreateUpdateBase):
    classroom_id = django_forms.IntegerField(
        required=False,
        label="Classroom ID",
        help_text="Unique identifier to be used for this classroom. "
        "If unspecified we will use the next ID available.",
    )

    field_order = ["classroom_id", "building", "room_number"]

    def clean_classroom_id(self) -> int:
        """
        Check the given classroom id does not already exist for the school.
        """
        classroom_id = self.cleaned_data.get("classroom_id")
        if queries.get_classrooms(
            school_id=self.school_id, classroom_id=classroom_id
        ).exists():
            next_available_id = queries.get_next_classroom_id_for_school(
                school_id=self.school_id
            )
            raise django_forms.ValidationError(
                f"Classroom with id: {classroom_id} already exists! "
                f"The next available id is: {next_available_id}"
            )
        return classroom_id
