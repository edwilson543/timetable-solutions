# Third party imports
from rest_framework import serializers

# Local application imports
from data import constants
from interfaces.utils import typing_utils


class UserProfile(serializers.Serializer):
    """
    Serializer a user and their associated profile.
    """

    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    approved_by_school_admin = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    def get_approved_by_school_admin(self, user: typing_utils.RegisteredUser) -> str:
        profile = user.profile
        if profile.approved_by_school_admin:
            return "Yes"
        return "No"

    def get_role(self, user: typing_utils.RegisteredUser) -> str:
        profile = user.profile
        return constants.UserRole(profile.role).label
