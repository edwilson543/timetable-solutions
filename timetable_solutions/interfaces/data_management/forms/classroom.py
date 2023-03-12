"""
Forms relating to the Teacher model.
"""

# Standard library imports
from typing import Any

# Django imports
from django import forms as django_forms

# Local application imports
from domain.data_management.classrooms import queries


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
