"""Module defining the model for a school_id classroom and any ancillary objects."""

# Standard library imports
from typing import Self

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.timetable_slot import TimetableSlot


class ClassroomQuerySet(models.QuerySet):
    """Custom queryset manager for the Classroom model"""

    def get_all_instances_for_school(self, school_id: int) -> models.QuerySet:
        """Method to return the full queryset of classrooms for a given school"""
        return self.filter(school_id=school_id)

    def get_individual_classroom(self, school_id: int, classroom_id: int) -> models.QuerySet:
        """Method to return an individual classroom instance"""
        return self.get(models.Q(school_id=school_id) & models.Q(classroom_id=classroom_id))


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

    # Introduce a custom manager
    objects = ClassroomQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the Classroom model
        """
        unique_together = [["school", "classroom_id"], ["school", "building", "room_number"]]

    class Constant:
        """
        Additional constants to store about the Classroom model (that aren't an option in Meta)
        """
        human_string_singular = "classroom"
        human_string_plural = "classrooms"

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.building},  {self.room_number}"

    def __repr__(self):
        """String representation of the model for debugging"""
        return f"Classroom: {self.school}: {self.classroom_id}"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, classroom_id: int, building: str, room_number: int) -> Self:
        """Method to create a new Classroom instance."""
        classroom = cls.objects.create(
            school_id=school_id, classroom_id=classroom_id, building=building, room_number=room_number)
        classroom.full_clean()
        return classroom

    # FILTER METHODS
    def check_if_occupied_at_time_slot(self, slot: TimetableSlot) -> bool:
        """
        Method to check whether the classroom has already been assigned a fixed class at the given slot.
        :return - True if OCCUPIED at the given timeslot.
        """
        # noinspection PyUnresolvedReferences
        slot_classes = self.classes.filter(time_slots=slot)
        n_commitments = slot_classes.count()
        if n_commitments == 1:
            return True
        elif n_commitments == 0:
            return False
        else:
            raise ValueError(f"Classroom {self.__str__}, {self.pk} has ended up with more than 1 FixedClass at {slot}")
