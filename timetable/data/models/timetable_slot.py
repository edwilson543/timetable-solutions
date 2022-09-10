"""Module defining the model for a timetable slot and any ancillary objects."""

# Standard library imports
import datetime as dt

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School


class TimetableSlot(models.Model):
    """Model for stating the unique timetable slots when classes can take place"""

    class WeekDay(models.TextChoices):
        MONDAY = "MONDAY"
        TUESDAY = "TUESDAY"
        WEDNESDAY = "WEDNESDAY"
        THURSDAY = "THURSDAY"
        FRIDAY = "FRIDAY"

    class PeriodStart(dt.time, models.Choices):
        PERIOD_ONE = 9, 0, "PERIOD_ONE"
        PERIOD_TWO = 10, 0, "PERIOD_TWO"
        PERIOD_THREE = 11, 0, "PERIOD_THREE"
        PERIOD_FOUR = 12, 0, "PERIOD_FOUR"
        LUNCH = 13, 0, "LUNCH"
        PERIOD_FIVE = 14, 0, "PERIOD_FIVE"
        PERIOD_SIX = 15, 0, "PERIOD_SIX"

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    slot_id = models.IntegerField()
    day_of_week = models.CharField(max_length=9, choices=WeekDay.choices)
    period_starts_at = models.TimeField(choices=PeriodStart.choices)
    period_duration = models.DurationField(default=dt.timedelta(hours=1))

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
