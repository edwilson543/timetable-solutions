"""
Module defining the model for a user profile in the database, and any ancillary objects.
Each Profile instance is used to add information relating to exactly one user.
"""

# Standard library imports
from typing import Self

# Django imports
from django.contrib.auth.models import User
from django.db import models

# Local application imports (other models)
from data.models.school import School


class UserRole(models.IntegerChoices):
    """
    Choices for the different roles that users can have with respect to the site.
    Note there is no interaction with the default Django authentication tiers (staff / superuser), these roles only
    relate to the custom admin.
    """
    SCHOOL_ADMIN = 1, "Administrator"  # Only role with access to the custom admin site
    TEACHER = 2, "Teacher"
    PUPIL = 3, "Pupil"


class Profile(models.Model):
    """
    Adds information to each User to provide additional profile data.
    Note that this information is currently just the school_id, since initial users are imagined as the teacher
    responsible for generating their school_id's timetables.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    role = models.IntegerField(choices=UserRole.choices, default=UserRole.SCHOOL_ADMIN.value)
    approved_by_school_admin = models.BooleanField(default=False)

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"Profile of: {self.user}"

    def __repr__(self):
        """String representation of the model for debugging"""
        return f"Profile of: {self.user}"

    # FACTORY METHODS
    @classmethod
    def create_and_save_new(cls, user: User, school_id: int, role: UserRole, approved_by_school_admin: bool) -> Self:
        """Method to create a new Profile instance, and then save it into the database"""
        profile = cls.objects.create(user=user, school_id=school_id, role=role,
                                     approved_by_school_admin=approved_by_school_admin)
        profile.full_clean()
        profile.save()
        return profile
