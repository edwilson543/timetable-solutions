"""The user/admin setup follows the 'extending the existing User model' section of django 4.0 docs."""

# Django imports
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Placeholder class to allow more easy future customisation of User class,"""
    pass


class TimetableLeadTeacher(models.Model):
    """
    Model representing the teacher in a school who is responsible for creating their school's timetables -
    this is the user who will upload data on their school to the database and run the solver.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school_access_key = models.SmallIntegerField()
