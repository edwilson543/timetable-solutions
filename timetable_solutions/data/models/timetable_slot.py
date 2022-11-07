"""Module defining the model for a timetable slot and any ancillary objects."""

# Standard library imports
import datetime as dt
from functools import lru_cache
from typing import Set, List

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School


class WeekDay(models.IntegerChoices):
    """Choices for the different days of the week a lesson can take place at"""
    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"


class TimetableSlotQuerySet(models.QuerySet):
    """
    Custom queryset manager for the TimetableSlot model.
    Note that this manager intentionally only includes filtration methods that return QuerySets
    """

    def get_all_instances_for_school(self, school_id: int) -> models.QuerySet:
        """Method returning the queryset of all timetable slots at the given school"""
        return self.filter(school_id=school_id)

    def get_individual_timeslot(self, school_id: int, slot_id: int):
        """Method returning an individual Teacher"""
        return self.get(models.Q(school_id=school_id) & models.Q(slot_id=slot_id))

    def get_specific_timeslots(self, school_id: int, slot_ids: Set[int]) -> models.QuerySet:
        """Method returning the slots at the given school, with the corresponding slot_ids"""
        return self.filter(models.Q(school_id=school_id) & models.Q(slot_id__in=slot_ids))

    def get_timeslots_on_given_day(self, school_id: int, day_of_week: WeekDay) -> models.QuerySet:
        """Method returning the timetable slots for the school on the given day of the week"""
        return self.filter(models.Q(school_id=school_id) & models.Q(day_of_week=day_of_week))


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

    class Constant:
        """
        Additional constants to store about the TimetableSlot model (that aren't an option in Meta)
        """
        human_string_singular = "timetable slot"
        human_string_plural = "timetable slots"

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"TimetableSlot {self.school}: {self.day_of_week}, {self.period_starts_at}"

    # FACTORIES
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
        slot.full_clean()
        return slot

    # QUERIES
    @classmethod
    @lru_cache(maxsize=8)
    def get_timeslot_ids_on_given_day(cls, school_id: int, day_of_week: WeekDay) -> List[int]:
        """
        Method returning the timetable slot IDs for the school on the given day of the week
        Method is cached since it's implicitly called form a list comp creating solver constraints on no repetition .
        """
        timeslots = cls.objects.get_timeslots_on_given_day(school_id=school_id, day_of_week=day_of_week)
        timeslot_ids = [timeslot.slot_id for timeslot in timeslots]
        return timeslot_ids
