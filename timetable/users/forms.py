# Django imports
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django import forms

# Local application imports
from data.models.school import School


class CustomUserCreationForm(UserCreationForm):
    """Placeholder customisation of the default django user creation form"""
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name")


class SchoolRegistrationPivot(forms.Form):
    """
    Pivot to decide whether the 2nd stage of user sign-up also requires them to register their school_id, or if
    they just need to enter their school_id access key. No doubt unnecessary with javascript...
    """
    CHOICES = [("EXISTING", "I have an existing school_id access key"),
               ("NEW", "I am registering my school_id for the first time")]
    existing_school = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label="")


class SchoolRegistrationForm(forms.ModelForm):
    """Form to fill in at registration, if the user also needs to register their school_id."""

    error_message = None

    class Meta:
        model = School
        fields = ["school_access_key", "school_name"]

    def is_valid(self):
        """Check that the requested school_id access key is taken and meets the requirements"""
        form_valid = super().is_valid()
        if not form_valid:
            self.error_message = self.errors["school_access_key"][0]  # Manually extract auto django form error
            return False
        access_key = self.cleaned_data.get("school_access_key")
        if len(str(access_key)) != 6:
            self.error_message = "Access key is not 6 digits"
            return False
        else:
            return True  # Access key available and is 6 digits


class ProfileRegistrationForm(forms.Form):
    """Form to fill in at registration, if the user's schools is already registered."""
    school_access_key = forms.IntegerField()
    error_message = None

    def is_valid(self):
        """Additional check on validity that the given access key exists."""
        form_valid = super().is_valid()
        if not form_valid:
            return False
        access_key = self.cleaned_data.get("school_access_key")

        if School.objects.filter(school_access_key=access_key).exists():
            return True
        else:
            self.error_message = "Access key not found, please try again"
            return False
