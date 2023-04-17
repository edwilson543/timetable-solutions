# Django imports
from django import forms
from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import models as django_models

# Local application imports
from data import constants, models


class UserCreation(auth_forms.UserCreationForm):
    """
    Add some fields from the Profile model to the user creation form.
    """

    class Meta(auth_forms.UserCreationForm.Meta):
        fields = auth_forms.UserCreationForm.Meta.fields + (
            "email",
            "first_name",
            "last_name",
        )


class SchoolRegistrationPivot(forms.Form):
    """
    Allow users to state whether they are registering to a new school or an existing one.
    """

    class NewUserType(django_models.TextChoices):
        EXISTING = "EXISTING", "I have an existing school access key"
        NEW = "NEW", "I am registering my school for the first time"

    existing_school = forms.ChoiceField(
        choices=NewUserType.choices, widget=forms.RadioSelect, label=""
    )


class SchoolRegistration(forms.Form):
    """
    Allow users to register a new school to the site.

    Note that the school access key is automatically generated.
    """

    school_name = forms.CharField(max_length=50)


class ProfileRegistration(forms.Form):
    """
    Form to fill in at registration, if the user's schools is already registered.
    """

    school_access_key = forms.IntegerField()
    position = forms.ChoiceField(choices=constants.UserRole.choices)

    error_message = None

    def is_valid(self) -> bool:
        """Additional check on validity that the given access key exists."""
        form_valid = super().is_valid()
        if not form_valid:
            return False
        access_key = self.cleaned_data.get("school_access_key")

        try:
            models.School.objects.get_individual_school(school_id=access_key)
            return True

        except ObjectDoesNotExist:
            self.error_message = "Access key not found, please try again"
            return False
