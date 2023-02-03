"""Module defining the model for a pupil and any ancillary objects."""

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.timetable_slot import TimetableSlot, TimetableSlotQuerySet
from data.models.year_group import YearGroup


class PupilQuerySet(models.QuerySet):
    """Custom queryset manager for the Pupil model"""

    def get_all_instances_for_school(self, school_id: int) -> "PupilQuerySet":
        """Method returning the queryset of pupils registered at the given school"""
        return self.filter(school_id=school_id)

    def get_specific_pupils(
        self, school_id: int, pupil_ids: set[int]
    ) -> "PupilQuerySet":
        """Method returning a queryset of pupils with the passed set of ids"""
        return self.filter(
            models.Q(school_id=school_id) & models.Q(pupil_id__in=pupil_ids)
        )

    def get_individual_pupil(self, school_id: int, pupil_id: int) -> "Pupil":
        """Method returning an individual Pupil"""
        return self.get(models.Q(school_id=school_id) & models.Q(pupil_id=pupil_id))


class Pupil(models.Model):
    """
    Model for storing pupils at all registered schools.
    """

    # Model fields
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    pupil_id = models.IntegerField()
    firstname = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    year_group = models.ForeignKey(
        YearGroup, on_delete=models.CASCADE, related_name="pupils"
    )

    # Introduce a custom manager
    objects = PupilQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the Pupil model
        """

        ordering = ["surname", "firstname"]
        unique_together = [["school", "pupil_id"]]

    class Constant:
        """
        Additional constants to store about the Pupil model (that aren't an option in Meta)
        """

        human_string_singular = "pupil"
        human_string_plural = "pupils"

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"{self.surname}, {self.firstname}"

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return f"{self.surname}, {self.firstname}"

    # --------------------
    # Factories
    # --------------------

    @classmethod
    def create_new(
        cls,
        school_id: int,
        pupil_id: int,
        firstname: str,
        surname: str,
        year_group_id: int,
    ) -> "Pupil":
        """Method to create a new Pupil instance."""
        year_group = YearGroup.objects.get_individual_year_group(
            school_id=school_id, year_group_id=year_group_id
        )

        pupil = cls.objects.create(
            school_id=school_id,
            pupil_id=pupil_id,
            firstname=firstname,
            surname=surname,
            year_group=year_group,
        )
        pupil.full_clean()
        return pupil

    @classmethod
    def delete_all_instances_for_school(cls, school_id: int) -> tuple:
        """
        Method to delete all the Pupil instances associated with a particular school
        """
        instances = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = instances.delete()
        return outcome

    # --------------------
    # Queries
    # --------------------

    def check_if_busy_at_timeslot(self, slot: TimetableSlot) -> bool:
        """
        Method to check whether the given pupil has already been assigned a lesson at the given slot.
        :return - True if BUSY at the given timeslot.
        """
        user_defined_slots = TimetableSlot.objects.filter(user_lessons__pupils=self)
        lesson_clashes = user_defined_slots.filter_for_clashes(slot)

        break_clashes = self.year_group.breaks.filter_for_clashes(slot)

        n_commitments = lesson_clashes.count() + break_clashes.count()

        if n_commitments == 1:
            return True
        elif n_commitments == 0:
            return False
        else:
            raise ValueError(
                f"Pupil {self.__str__}, {self.pk} has ended up with more than 1 lesson at {slot}"
            )

    def get_associated_timeslots(self) -> TimetableSlotQuerySet:
        """
        Method to return the TimetableSlot instances relevant to a pupil
        """
        return self.year_group.slots.all()

    def get_lessons_per_week(self) -> int:
        """
        Method to get the number of lessons a pupil has per week.
        """
        return sum(lesson.total_required_slots for lesson in self.lessons.all())

    def get_occupied_percentage(self) -> float:
        """
        Method to get the percentage of time a pupil is occupied (including any lunch slots)
        """
        n_associated_slots = self.get_associated_timeslots().count()
        return self.get_lessons_per_week() / n_associated_slots
