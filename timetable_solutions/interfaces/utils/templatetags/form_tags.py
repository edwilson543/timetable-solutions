"""
Custom template tags and filters related to form rendering.
"""

# Standard library imports
import collections
import datetime as dt
from typing import Any

# Django imports
from django import forms, template

register = template.Library()


@register.filter(name="is_basic_input_widget")
def is_basic_input_widget(field: forms.BoundField | forms.Field) -> bool:
    """
    Check if an input widget should be rendered using a simple <input type="x">.
    """
    basic_input_fields = ["text", "number", "time", "email", "password"]

    widget_type = None
    if isinstance(field, forms.BoundField):
        widget_type = field.widget_type
    if isinstance(field, forms.Field):
        widget_type = field.widget.input_type
    return widget_type in basic_input_fields


@register.filter(name="is_string")
def is_string(value: Any) -> bool:
    """
    Test if some context variable is a string.
    """
    return isinstance(value, str)


@register.filter(name="is_time")
def is_time(value: Any) -> bool:
    """
    Test if some context variable is a datetime time.
    """
    return isinstance(value, dt.time)


@register.simple_tag(name="get_object_id")
def get_object_id(serialized_model_instance: collections.OrderedDict) -> int | str:
    """
    Test if some context variable is a datetime time.
    """
    # Should have called them all the same, 'id_within_school'
    for id_field_name in [
        "break_id",
        "classroom_id",
        "lesson_id",
        "pupil_id",
        "slot_id",
        "teacher_id",
        "year_group_id",
    ]:
        if object_id := serialized_model_instance.get(id_field_name, None):
            return object_id
    raise ValueError(
        "Serialized model instance given in get_object_id template tag did not have a valid id field."
    )
