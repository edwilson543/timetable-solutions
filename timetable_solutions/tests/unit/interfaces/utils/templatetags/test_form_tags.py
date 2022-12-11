"""
Unit tests for the custom form tags.
"""

# Standard library imports
from typing import Type

# Third party imports
import pytest

# Django imports
from django import forms
from django import template
from django.utils import html


@pytest.fixture(scope="module")
def form() -> Type[forms.Form]:
    """
    Fixture to provide a dummy form for use in tests.
    """
    class TestForm(forms.Form):
        text = forms.CharField()
    return TestForm


def test_render_form_field_in_div_renders_text_field_correctly(form: Type[forms.Form]):
    """
    Test that the correct html is returned from the 'text' field.
    """
    # Set test parameters
    template_string = """
    {% load form_tags %}
    {% field_div form.text %}
    """
    temp = template.Template(template_string=template_string)
    context = template.Context({"form": form})

    # Execute test unit
    outcome = temp.render(context=context)

    # Check outcome
    expected_html = html.SafeString("""
    <div>
        <label for="id_text">Text:</label>
        <div class="helptext">
        </div>
        <input type="text" name="text" required id="id_text">
    </div>
    """)
    assert isinstance(outcome, html.SafeString)
    assert expected_html in outcome
