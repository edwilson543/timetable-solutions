# Third party imports
import pytest

# Django imports
from django.contrib.auth import models as auth_models

# Local application imports
from data import constants, models
from domain.users import operations
from tests import data_factories


@pytest.mark.django_db
class TestUpdateUser:
    def test_updates_user_and_profile_all_parameters(self):
        profile = data_factories.Profile()
        user = profile.user

        updated_user = operations.update_user(
            user,
            first_name="Ed",
            last_name="Wilson",
            email="ed@test.com",
            role=constants.UserRole.TEACHER,
            approved_by_school_admin=True,
        )

        assert updated_user.first_name == "Ed"
        assert updated_user.last_name == "Wilson"
        assert updated_user.email == "ed@test.com"

        updated_profile = updated_user.profile
        assert updated_profile.role == constants.UserRole.TEACHER
        assert updated_profile.approved_by_school_admin

    def test_updates_subset_of_parameters_only(self):
        profile = data_factories.Profile(approved_by_school_admin=False)
        user = profile.user

        updated_user = operations.update_user(user, approved_by_school_admin=True)

        updated_profile = updated_user.profile
        assert updated_profile.approved_by_school_admin


@pytest.mark.django_db
class TestDeleteUser:
    def test_deletes_user_and_profile(self):
        profile = data_factories.Profile()
        user = profile.user

        operations.delete_user(user)

        with pytest.raises(auth_models.User.DoesNotExist):
            user.refresh_from_db()

        with pytest.raises(models.Profile.DoesNotExist):
            profile.refresh_from_db()
