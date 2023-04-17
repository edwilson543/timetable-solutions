# Third party imports
import pytest

# Django imports
from django.core import exceptions

# Local application imports
from interfaces.users import forms
from tests import data_factories


@pytest.mark.django_db
class TestProfileRegistrationCleanSchoolAccessKey:
    def test_valid_access_key_allowed(self):
        school = data_factories.School()

        form = forms.ProfileRegistration()
        form.cleaned_data = {"school_access_key": school.school_access_key}

        clean_access_key = form.clean_school_access_key()

        assert clean_access_key == school.school_access_key

    def test_invalid_access_key_raises_validation_error(self):
        form = forms.ProfileRegistration()
        form.cleaned_data = {"school_access_key": 123456}

        with pytest.raises(exceptions.ValidationError) as exc:
            form.clean_school_access_key()

        assert "Invalid school access key" in exc.value
