"""Module defining the model for a school_id classroom and any ancillary objects."""

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
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    classroom_id = models.IntegerField()
    building = models.CharField(max_length=20)
    room_number = models.IntegerField()

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.building},  {self.room_number}"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, classroom_id: int, building: str, room_number: int):
        """Method to create a new Classroom instance."""
        classroom = cls.objects.create(
            school_id=school_id, classroom_id=classroom_id, building=building, room_number=room_number)
        return classroom
