"""Module defining the model for a school in the database, and any ancillary objects"""

# Django imports
from django.db import models


class School(models.Model):
    """Model representing a school, with every other model associated with one school instance via a foreign key"""
    school_access_key = models.SmallIntegerField(primary_key=True)
    school_name = models.CharField(max_length=50)
