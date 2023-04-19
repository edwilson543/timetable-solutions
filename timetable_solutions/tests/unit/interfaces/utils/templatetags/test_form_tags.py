"""
Unit tests for the custom form tags.
"""


# Third party imports
import pytest

# Django imports
from django import forms, template
from django.utils import html


@pytest.fixture(scope="module")
def form() -> type[forms.Form]:
    """
    Fixture to provide a dummy form for use in tests.
    """

    class TestForm(forms.Form):
        text = forms.CharField()

    return TestForm


def test_render_form_field_in_div_renders_text_field_correctly(form: type[forms.Form]):
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
    expected_html = html.SafeString(
        """
    <div>
        <label for="id_text">Text:</label>
        <div class="helptext">
        </div>
        <input type="text" name="text" required id="id_text">
    </div>
    """
    )
    assert isinstance(outcome, html.SafeString)
    assert expected_html in outcome


class TestIsBasicInputWidget:
    @pytest.mark.parametrize(
        "field, expected_return",
        [
            (forms.CharField(), True),
            (forms.IntegerField(), True),
            (forms.TimeField(), True),
            (forms.CharField(widget=forms.PasswordInput()), True),
            (forms.EmailField(), True),
            (forms.ChoiceField(), False),
            (forms.CheckboxInput(), False),
            (forms.FileField(), False),
        ],
    )
    def test_is_basic_input_widget_unbound_field(
        self, field: forms.Field, expected_return: bool
    ):
        template_string = """
        {% load form_tags %}
        {% if field|is_basic_input_widget %}
            <p>Is text or number input</p>
        {% endif %}
        {{ field|is_basic_input_widget }}
        """

        temp = template.Template(template_string=template_string)
        context = template.Context({"field": field})

        outcome = temp.render(context=context)

        if expected_return:
            assert "Is text or number input" in outcome
            assert "True" in outcome
        else:
            assert "Is text or number input" not in outcome
            assert "False" in outcome

    def test_is_basic_input_widget_bound_field(self):
        class Form(forms.Form):
            text = forms.CharField()

        form = Form(data={"text": "test"})

        template_string = """
        {% load form_tags %}
        {% if form.text|is_basic_input_widget %}
            <p>Is text or number input</p>
        {% endif %}
        {{ form.text|is_basic_input_widget }}
        """

        temp = template.Template(template_string=template_string)
        context = template.Context({"form": form})

        outcome = temp.render(context=context)

        assert "Is text or number input" in outcome
        assert "True" in outcome
