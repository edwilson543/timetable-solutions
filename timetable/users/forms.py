# Django imports
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django import forms

# Local application imports
from .models import School


class CustomUserCreationForm(UserCreationForm):
    """Placeholder customisation of the default django user creation form"""
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name")


class SchoolRegistrationPivot(forms.Form):
    """
    Pivot to decide whether the 2nd stage of user sign-up also requires them to register their school, or if
    they just need to enter their school access key. No doubt unnecessary with javascript...
    """
    CHOICES = [("EXISTING", "I have an existing school access key"),
               ("NEW", "I am registering my school for the first time")]
    existing_school = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label="")


class SchoolRegistrationForm(forms.ModelForm):
    """Form to fill in at registration, if the user also needs to register their school."""

    error_message = None

    class Meta:
        model = School
        fields = ["school_access_key", "school_name"]

    def is_valid(self):
        """Check that the requested school access key is taken and meets the requirements"""
        form_valid = super().is_valid()
        if not form_valid:
            return False
        access_key = self.cleaned_data.get("school_access_key")
        try:
            access_key_exists = School.objects.get(school_access_key=access_key)
            self.error_message = "Access key already taken"
            return False  # Access key already taken so form is not valid
        except ObjectDoesNotExist:  # The access key is available, so form might be valid
            if len(str(access_key)) == 6:
                return True  # Access key available and is 6 digits
            else:
                self.error_message = "Access key is not 6 digits"
                return False


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
        try:
            access_key_exists = School.objects.get(school_access_key=access_key)
            return True
        except ObjectDoesNotExist:
            self.error_message = "Access key not found, please try again"
            return False
