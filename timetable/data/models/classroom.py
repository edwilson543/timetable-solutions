from django.db import models

from data.models import School


class Classroom(models.Model):
    """
    Model storing the classroom (location) in which a fixed class takes place.
    Currently, a fixed class id must take place in exactly one classroom
    """
    classroom_id = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    building = models.CharField(max_length=20)
    room_number = models.IntegerField()