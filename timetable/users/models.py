"""Models used to define the users of the application."""

# Django imports
from django.contrib.auth.models import User
from django.db import models


class School(models.Model):
    """Model representing a school, which all other models become associated with"""
    school_access_key = models.SmallIntegerField(primary_key=True)
    school_name = models.CharField(max_length=50)


class Profile(models.Model):
    """
    Extends User to provide additional profile data - currently just information on the school, since initial users are
    imagined as the teacher responsible for generating their timetable.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
