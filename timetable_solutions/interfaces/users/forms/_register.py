"""
Forms used for the registration of new users.
"""

# Django imports
from django import forms
from django.contrib.auth import forms as auth_forms
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
    Allow users to register themselves to an existing school.
    """

    school_access_key = forms.IntegerField()
    position = forms.ChoiceField(choices=constants.UserRole.choices)

    def clean_school_access_key(self) -> int:
        """
        Additional check on validity that the given access key exists.
        """
        school_access_key = self.cleaned_data.get("school_access_key")
        try:
            models.School.objects.get_individual_school(school_id=school_access_key)
        except models.School.DoesNotExist:
            raise forms.ValidationError("Invalid school access key")
        return school_access_key
