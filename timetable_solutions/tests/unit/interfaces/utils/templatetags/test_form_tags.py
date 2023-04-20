"""
Unit tests for the custom form tags and filters.
"""

# Third party imports
import pytest

# Django imports
from django import forms, template


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
