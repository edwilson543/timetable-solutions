# Standard library imports
from collections import OrderedDict

# Third party imports
import pytest

# Django imports
from django.contrib.auth import models as auth_models

# Local application imports
from data import constants
from interfaces.constants import UrlName
from interfaces.users import serializers
from tests import data_factories


@pytest.mark.django_db
class TestUserProfile:
    def test_serialize_single_user(self):
        profile = data_factories.Profile(approved_by_school_admin=True)
        user = profile.user

        serialized_user = serializers.UserProfile(user).data

        assert serialized_user == OrderedDict(
            [
                ("username", user.username),
                ("first_name", user.first_name),
                ("last_name", user.last_name),
                ("email", user.email),
                ("approved_by_school_admin", "Yes"),
                ("role", constants.UserRole(profile.role).label),
                ("update_url", UrlName.USER_UPDATE.url(username=user.username)),
            ]
        )

    def test_serialize_multiple_users(self):
        profile = data_factories.Profile(approved_by_school_admin=True)
        user = profile.user

        other_profile = data_factories.Profile(approved_by_school_admin=False)
        other_user = other_profile.user

        all_users = auth_models.User.objects.all()

        serialized_users = serializers.UserProfile(all_users, many=True).data

        assert serialized_users == [
            OrderedDict(
                [
                    ("username", user.username),
                    ("first_name", user.first_name),
                    ("last_name", user.last_name),
                    ("email", user.email),
                    ("approved_by_school_admin", "Yes"),
                    ("role", constants.UserRole(profile.role).label),
                    ("update_url", UrlName.USER_UPDATE.url(username=user.username)),
                ]
            ),
            OrderedDict(
                [
                    ("username", other_user.username),
                    ("first_name", other_user.first_name),
                    ("last_name", other_user.last_name),
                    ("email", other_user.email),
                    ("approved_by_school_admin", "No"),
                    ("role", constants.UserRole(other_profile.role).label),
                    (
                        "update_url",
                        UrlName.USER_UPDATE.url(username=other_user.username),
                    ),
                ]
            ),
        ]
