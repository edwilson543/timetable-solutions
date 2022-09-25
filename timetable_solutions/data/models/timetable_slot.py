"""Module defining the model for a timetable slot and any ancillary objects."""

# Standard library imports
import datetime as dt

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


class TimetableSlot(models.Model):
    """Model for stating the unique timetable slots when classes can take place"""

    class WeekDay(models.TextChoices):
        """Choices for the different days of the week a lesson can take place at"""
        MONDAY = "MONDAY"
        TUESDAY = "TUESDAY"
        WEDNESDAY = "WEDNESDAY"
        THURSDAY = "THURSDAY"
        FRIDAY = "FRIDAY"

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    slot_id = models.IntegerField()
    day_of_week = models.CharField(max_length=9, choices=WeekDay.choices)
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
        slot = cls.objects.create(school_id=school_id, slot_id=slot_id, day_of_week=day_of_week,
                                  period_starts_at=period_starts_at, period_duration=period_duration)
        return slot
