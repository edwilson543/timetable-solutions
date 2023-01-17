"""
Unit tests for the ProfileAdmin.
"""

# Third party imports
import pytest

# Django imports
from django import test

# Local application imports
from data import models
from interfaces.custom_admin import admin
from tests import factories


@pytest.mark.django_db
class TestBaseModelAdmin:
    def test_approve_user_accounts(self):
        """
        Test that the admin can approve user accounts (profiles) using the admin action.
        """
        # Make an admin user profile
        admin_profile = factories.Profile(school_admin=True)

        # Add an unapproved user profile to the same school
        unapproved_profile = factories.Profile(
            school=admin_profile.school, approved_by_school_admin=False
        )

        # Create a request to the admin profile page
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/profile/")
        request.user = admin_profile.user
        profile_model_admin = admin.ProfileAdmin(
            model=models.Profile, admin_site=admin.user_admin
        )

        # Simulate approving the unapproved profiles
        profile_queryset = models.Profile.objects.get_all_instances_for_school(
            school_id=admin_profile.school.school_access_key
        )
        assert unapproved_profile in profile_queryset
        profile_model_admin.approve_user_accounts(
            request=request, queryset=profile_queryset
        )

        # Check the unapproved profile is now approved - note the instance in memory will not have been updated,
        # so we need to retrieve from the db
        unapproved_profile = models.Profile.objects.get(
            user__username=unapproved_profile.username
        )
        assert unapproved_profile.approved_by_school_admin is True

    def test_get_actions(self):
        """
        Test that all actions are registered, with the correct names
        """
        # Make an admin user profile
        admin_profile = factories.Profile(school_admin=True)

        # Create a request to the admin profile page
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/profile/")
        request.user = admin_profile.user
        profile_admin = admin.ProfileAdmin(
            model=models.Profile, admin_site=admin.user_admin
        )

        # Get the available actions
        actions = profile_admin.get_actions(request=request)

        # Inspect the available actions
        assert set(actions.keys()) == {"delete_selected", "approve_user_accounts"}

        # INDEXES are: callback = 0; name = 1; short_description = 2;
        assert actions["delete_selected"][2] == "Delete selected users"
        assert actions["approve_user_accounts"][1]

    def test_get_queryset_filters_by_school(self):
        """
        Test that the queryset of user profiles shown to a user is restricted to their school only.
        """
        # Add a test user, a profile they should, and a profile they shouldn't be able to see
        test_user = factories.User()
        test_profile = factories.Profile(user=test_user)

        hidden_profile = factories.Profile()

        # Create a request to the admin index page
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/profile/")
        request.user = test_user
        profile_admin = admin.ProfileAdmin(
            model=models.Profile, admin_site=admin.user_admin
        )

        # Retrieve the profiles the test user can see
        viewable_profiles = profile_admin.get_queryset(request=request)

        # Check only the test profile is included in the queryset
        assert test_profile in viewable_profiles
        assert hidden_profile not in viewable_profiles
