"""
Module defining the model for a user profile in the database, and any ancillary objects.
Each Profile instance is used to add information relating to exactly one user.
"""

# Standard library imports
from typing import Optional

# Django imports
from django.contrib.auth.models import User
from django.db import models

# Local application imports (other models)
from data import constants
from data.models.school import School


class ProfileQuerySet(models.QuerySet):
    """Custom queryset manager for the Profile model"""

    def get_all_instances_for_school(self, school_id: int) -> "ProfileQuerySet":
        """
        Method returning the queryset of profiles registered at the given school
        """
        return self.filter(school_id=school_id)

    def get_individual_profile(self, username: str) -> Optional["Profile"]:
        """
        Method returning a Profile instance when looked up by username
        """
        users = self.filter(user__username=username)
        if users.exists():
            return users.first()
        else:
            return None

    def mark_selected_users_as_approved(self) -> None:
        """
        Method updating each Profile in a queryset to be approved by the school admin.
        """
        self.update(approved_by_school_admin=True)


class Profile(models.Model):
    """
    Adds information to each User to provide additional profile data.
    Note that this information is currently just the school_id, since initial users are imagined as the teacher
    responsible for generating their school_id's timetables.
    """

    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    role = models.IntegerField(
        choices=constants.UserRole.choices, default=constants.UserRole.SCHOOL_ADMIN
    )
    approved_by_school_admin = models.BooleanField(default=False)

    # Introduce a custom admin
    objects = ProfileQuerySet.as_manager()

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"{self.user} profile"

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return f"{self.user} profile"

    # --------------------
    # Factories tests
    # --------------------

    @classmethod
    def create_new(
        cls,
        user: User,
        school_id: int,
        role: str | constants.UserRole,
        approved_by_school_admin: bool,
    ) -> "Profile":
        """Method to create a new Profile instance, and then save it into the database"""
        if isinstance(role, str):
            role = constants.UserRole(int(role))
        profile = cls.objects.create(
            user=user,
            school_id=school_id,
            role=role,
            approved_by_school_admin=approved_by_school_admin,
        )
        profile.full_clean()
        return profile

    # --------------------
    # Properties tests
    # --------------------

    @property
    def username(self) -> str:
        return self.user.username
