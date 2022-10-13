"""Module defining the model for a timetable slot and any ancillary objects."""

# Standard library imports
import datetime as dt
from typing import Set

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School


class TimetableSlotQuerySet(models.QuerySet):
    """Custom queryset manager for the TimetableSlot model"""

    def get_all_instances_for_school(self, school_id: int) -> models.QuerySet:
        """Method returning the queryset of all timetable slots at the given school"""
        return self.filter(school_id=school_id)

    def get_individual_timeslot(self, school_id: int, slot_id: int):
        """Method returning an individual Teacher"""
        return self.get(models.Q(school_id=school_id) & models.Q(slot_id=slot_id))

    def get_specific_timeslots(self, school_id: int, slot_ids: Set[int]):
        """Method returning the list of slots and the school with corresponding slot_id"""
        return self.filter(models.Q(school_id=school_id) & models.Q(slot_id__in=slot_ids))


class WeekDay(models.IntegerChoices):
    """Choices for the different days of the week a lesson can take place at"""
    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"


class TimetableSlot(models.Model):
    """Model for stating the unique timetable slots when classes can take place"""

    class Meta:
        """Additional information relating to this model"""
        ordering = ["day_of_week", "period_starts_at"]

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    slot_id = models.IntegerField()
    day_of_week = models.SmallIntegerField(choices=WeekDay.choices)
    period_starts_at = models.TimeField()
    period_duration = models.DurationField(default=dt.timedelta(hours=1))

    # Introduce a custom manager
    objects = TimetableSlotQuerySet.as_manager()

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.day_of_week}, {self.period_starts_at}"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, slot_id: int, day_of_week: str, period_starts_at: dt.time,
                   period_duration: dt.timedelta):
        """Method to create a new TimetableSlot instance."""
        try:
            day_of_week = int(day_of_week)
        except ValueError:
            raise ValueError(f"Tried to create TimetableSlot instance with day_of_week: {day_of_week} of type: "
                             f"{type(day_of_week)}")
        slot = cls.objects.create(school_id=school_id, slot_id=slot_id, day_of_week=day_of_week,
                                  period_starts_at=period_starts_at, period_duration=period_duration)
        return slot
