"""
Module defining custom template tags related to form rendering.
"""

# Standard library imports
import re
from typing import Any

# Django imports
from django import forms, template
from django.utils import html

register = template.Library()


@register.simple_tag(name="field_div")
def render_form_field_in_div(bound_field: forms.BoundField) -> html.SafeString:
    """
    # TODO -> DELETE!!!!!!!
    Template tag rendering the individual form field inside div elements.

    The HTML produced is the same as that produced by django's _html_output, which renders the entire form. It doesn't
    seem there's a snipped which just renders an individual form field.
    The use case is initially when adding htmx to forms, it's unideal to write out the html for every field
    manually. So the one's we want to add htmx to get written manually, the rest use this tag.

    :param bound_field - the field of the form being rendered
    :return the string formatted as a SafeString, using html
    """
    text = f"""
    <div>
        { bound_field.label_tag() }
        <div class="helptext">
            { bound_field.help_text }
        </div>
        { bound_field.errors }
        { bound_field }
    </div>
    """
    text = text.strip()
    text = re.sub(r"\n\s*\n", "\n", text)
    return html.format_html(text)


@register.filter(name="is_text_or_number_input")
def is_text_or_number_input(field: forms.BoundField | forms.Field) -> bool:
    """
    Check if an input widget is for a text or number input field.
    These are both marked up in the same way.
    """
    if isinstance(field, forms.BoundField):
        return (field.widget_type == "text") or (field.widget_type == "number")
    elif isinstance(field, forms.Field):
        return (field.widget.input_type == "text") or (
            field.widget.input_type == "number"
        )
    return False


@register.filter(name="is_string")
def is_string(value: Any) -> bool:
    """
    Test if some context variable is a string.
    """
    return isinstance(value, str)
