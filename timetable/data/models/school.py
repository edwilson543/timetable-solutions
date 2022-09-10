"""Module defining the model for a school_id in the database, and any ancillary objects"""

# Django imports
from django.db import models


class School(models.Model):
    """
    Model representing a school_id, with every other model associated with one school_id instance via a foreign key
    """
    school_access_key = models.SmallIntegerField(primary_key=True)
    school_name = models.CharField(max_length=50)

    def __str__(self):
        """String representation of the model for the django admin site"""
        return self.school_name

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_access_key: int, school_name: str):
        """Method to create a new School instance."""
        school = cls.objects.create(school_access_key=school_access_key, school_name=school_name)
        return school
