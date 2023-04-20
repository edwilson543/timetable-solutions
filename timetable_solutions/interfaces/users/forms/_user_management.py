# Django imports
from django import forms as django_forms

# Local application imports
from data import constants


class UpdateUser(django_forms.Form):
    """
    Form to update a user and their profile with.
    """

    first_name = django_forms.CharField(max_length=150)
    last_name = django_forms.CharField(max_length=150)
    email = django_forms.EmailField()
    approved_by_school_admin = django_forms.BooleanField()
    role = django_forms.ChoiceField(choices=constants.UserRole.choices)
