"""
Module defining the model for a user profile in the database, and any ancillary objects.
A each Profile instance is used to add information relating to exactly one user.
"""

# Django imports
from django.contrib.auth.models import User
from django.db import models

# Local application imports (other models)
from data.models.school import School


class Profile(models.Model):
    """
    Adds information to each User to provide additional profile data.
    Note that this information is currently just the school, since initial users are imagined as the teacher
    responsible for generating their school's timetables.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)