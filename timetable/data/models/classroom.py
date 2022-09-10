"""Module defining the model for a school classroom and any ancillary objects."""

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School


class Classroom(models.Model):
    """
    Model storing the classroom (location) in which a FixedClass/UnsolvedClass takes place.
    Currently, a fixed class id must take place in exactly one classroom - a future extension could be to also optimise
    based on minimising the number of distinct classrooms required.
    """
    classroom_id = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    building = models.CharField(max_length=20)
    room_number = models.IntegerField()
