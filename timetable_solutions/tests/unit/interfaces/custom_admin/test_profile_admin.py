"""
Unit tests for the ProfileAdmin.
"""

# Django imports
from django import test
from django.contrib.auth.models import User

# Local application imports
from data import models
from interfaces.custom_admin import admin


class TestBaseModelAdmin(test.TestCase):

    fixtures = [
        "user_school_profile.json",
        "classrooms.json",
        "pupils.json",
        "teachers.json",
        "timetable.json",
        "lessons_with_solution.json",
    ]

    def test_approve_user_accounts(self):
        """
        Test that the admin can approve user accounts (profiles) using the admin action.
        """
        # Add an approved user to the same school
        other_user = User.objects.create_user(username="test", password="test")
        models.Profile.create_and_save_new(
            user=other_user,
            school_id=123456,
            role=models.UserRole.TEACHER,
            approved_by_school_admin=False,
        )

        # Create a request to the admin index page
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/profile/")
        request.user = User.objects.get(username="dummy_teacher")
        profile_admin = admin.ProfileAdmin(
            model=models.Profile, admin_site=admin.user_admin
        )

        # Execute test unit
        profile_queryset = models.Profile.objects.get_all_instances_for_school(
            school_id=123456
        )
        profile_admin.approve_user_accounts(request=request, queryset=profile_queryset)

        # Check outcome
        profile = models.Profile.objects.get_individual_profile(username="test")
        assert profile.approved_by_school_admin

    def test_get_actions(self):
        """
        Test that all actions are registered, with the correct names
        """
        # Set test parameters
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/profile/")
        request.user = User.objects.get(username="dummy_teacher")
        profile_admin = admin.ProfileAdmin(
            model=models.Profile, admin_site=admin.user_admin
        )

        # Execute test unit
        actions = profile_admin.get_actions(request=request)

        # Check outcome
        assert set(actions.keys()) == {"delete_selected", "approve_user_accounts"}
        # INDEXES: callback = 0; name = 1; short_description = 2;
        assert actions["delete_selected"][2] == "Delete selected users"
        assert actions["approve_user_accounts"][1]

    def test_get_queryset_filters_by_school(self):
        """
        Test that the queryset of user profiles for a user of school 123456 is restricted to their school only.
        """
        # Add a user for another school
        other_user = User.objects.create_user(username="test", password="test")
        models.School.create_new(school_name="test", school_access_key=100001)
        models.Profile.create_and_save_new(
            user=other_user,
            school_id=100001,
            role=models.UserRole.TEACHER,
            approved_by_school_admin=False,
        )

        # Create a request to the admin index page
        factory = test.RequestFactory()
        request = factory.get("/data/admin/data/profile/")
        request.user = User.objects.get(username="dummy_teacher")
        profile_admin = admin.ProfileAdmin(
            model=models.Profile, admin_site=admin.user_admin
        )

        # Execute test unit
        queryset = profile_admin.get_queryset(request=request)

        # Check outcome
        expected_queryset = models.Profile.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert queryset.count() == 1
        self.assertQuerysetEqual(queryset, expected_queryset, ordered=False)
