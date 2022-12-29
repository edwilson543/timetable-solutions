# Django imports
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django import forms

# Local application imports
from data import models


class CustomUserCreation(UserCreationForm):
    """Placeholder customisation of the default django user creation form"""
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name")


class SchoolRegistrationPivot(forms.Form):
    """
    Pivot to decide whether the 2nd stage of user sign-up also requires them to register their school_id, or if
    they just need to enter their school_id access key.
    """
    CHOICES = [
        ("EXISTING", "I have an existing school access key"),
        ("NEW", "I am registering my school for the first time")
    ]

    existing_school = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label="")


class SchoolRegistration(forms.Form):
    """
    Form to fill in at registration, when the user needs to register their school for the first time.
    All the user needs to enter is the school's name - the access key is automatically generated.
    """
    school_name = forms.CharField(max_length=100)


class ProfileRegistration(forms.Form):
    """
    Form to fill in at registration, if the user's schools is already registered.
    """
    ROLE_CHOICES = [
        # mypy doesn't recognise the value / label attributes of UserRole(IntegerChoices)
        (models.UserRole.TEACHER.value, models.UserRole.TEACHER.label),  # type: ignore
        (models.UserRole.PUPIL.value, models.UserRole.PUPIL.label)  # type: ignore
    ]

    school_access_key = forms.IntegerField()
    position = forms.ChoiceField(choices=ROLE_CHOICES)

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
