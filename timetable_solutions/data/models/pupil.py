"""Module defining the model for a pupil and any ancillary objects."""

# Standard library imports
from typing import Self, Set

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.timetable_slot import TimetableSlot


class PupilQuerySet(models.QuerySet):
    """Custom queryset manager for the Pupil model"""

    def get_all_instances_for_school(self, school_id: int) -> models.QuerySet:
        """Method returning the queryset of pupils registered at the given school"""
        return self.filter(school_id=school_id)

    def get_school_year_group(self, school_id: int, year_group: int) -> models.QuerySet:
        """method returning the queryset of pupils belonging to a specific school and year group"""
        query_set = self.filter(models.Q(school_id=school_id) & models.Q(year_group=year_group))
        query_set.order_by("surname")
        return query_set

    def get_specific_pupils(self, school_id: int, pupil_ids: Set[int]) -> models.QuerySet:
        """Method returning a queryset of pupils with the passed set of ids"""
        return self.filter(models.Q(school_id=school_id) & models.Q(pupil_id__in=pupil_ids))

    def get_individual_pupil(self, school_id: int, pupil_id: int):
        """Method returning an individual Pupil"""
        return self.get(models.Q(school_id=school_id) & models.Q(pupil_id=pupil_id))


class Pupil(models.Model):
    """
    Model for storing pupils at all registered schools.
    """

    class YearGroup(models.IntegerChoices):
        ONE = 1, "One"
        TWO = 2, "Two"
        THREE = 3, "Three"
        FOUR = 4, "Four"
        FIVE = 5, "Five"
        SIX = 6, "Six"
        SEVEN = 7, "Seven"
        EIGHT = 8, "Eight"
        NINE = 9, "Nine"
        TEN = 10, "Ten"

    # Model fields
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    pupil_id = models.IntegerField()
    firstname = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    year_group = models.IntegerField(choices=YearGroup.choices)

    # Introduce a custom manager
    objects = PupilQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the Pupil model
        """
        unique_together = [["school", "pupil_id"]]

    class Constant:
        """
        Additional constants to store about the Pupil model (that aren't an option in Meta)
        """
        human_string_singular = "pupil"
        human_string_plural = "pupils"

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.surname}, {self.firstname}"

    def __repr__(self):
        """String representation of the model for debugging"""
        return f"Pupil {self.school}: {self.pupil_id}"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, pupil_id: int, firstname: str, surname: str, year_group: int) -> Self:
        """Method to create a new Pupil instance."""
        year_group = cls.YearGroup(year_group).value
        pupil = cls.objects.create(school_id=school_id, pupil_id=pupil_id, firstname=firstname, surname=surname,
                                   year_group=year_group)
        pupil.full_clean()
        return pupil

    # FILTER METHODS
    def check_if_busy_at_time_slot(self, slot: TimetableSlot) -> bool:
        """
        Method to check whether the given pupil has already been assigned a fixed class at the given slot.
        :return - True if BUSY at the given timeslot.
        """
        # noinspection PyUnresolvedReferences
        slot_classes = self.classes.filter(time_slots=slot)
        n_commitments = slot_classes.count()
        if n_commitments == 1:
            return True
        elif n_commitments == 0:
            return False
        else:
            raise ValueError(f"Pupil {self.__str__}, {self.pk} has ended up with more than 1 FixedClass at {slot}")
