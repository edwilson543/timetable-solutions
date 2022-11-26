"""Module defining the model for a timetable slot and any ancillary objects."""

# Standard library imports
import datetime as dt
from functools import lru_cache
from typing import List, Self, Set, Tuple

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

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    slot_id = models.IntegerField()
    day_of_week = models.SmallIntegerField(choices=WeekDay.choices)
    period_starts_at = models.TimeField()
    period_duration = models.DurationField(default=dt.timedelta(hours=1))

    # Introduce a custom manager
    objects = TimetableSlotQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the TimetableSlot model
        """
        ordering = ["day_of_week", "period_starts_at"]
        unique_together = [["school", "slot_id"]]

    class Constant:
        """
        Additional constants to store about the TimetableSlot model (that aren't an option in Meta)
        """
        human_string_singular = "timetable slot"
        human_string_plural = "timetable slots"

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"TimetableSlot {self.school}: {self.day_of_week}, {self.period_starts_at}"

    def __repr__(self):
        """String representation of the model for debugging"""
        return f"TimetableSlot {self.school}: {self.day_of_week}, {self.period_starts_at}"

    # FACTORIES
    @classmethod
    def create_new(cls, school_id: int, slot_id: int, day_of_week: WeekDay, period_starts_at: dt.time,
                   period_duration: dt.timedelta) -> Self:
        """Method to create a new TimetableSlot instance."""
        try:
            day_of_week = WeekDay(day_of_week).value
        except ValueError:
            raise ValueError(f"Tried to create TimetableSlot instance with day_of_week: {day_of_week} of type: "
                             f"{type(day_of_week)}")
        slot = cls.objects.create(school_id=school_id, slot_id=slot_id, day_of_week=day_of_week,
                                  period_starts_at=period_starts_at, period_duration=period_duration)
        slot.full_clean()
        return slot

    @classmethod
    def delete_all_instances_for_school(cls, school_id: int) -> Tuple:
        """
        Method to delete all the TimetableSlot instances associated with a particular school
        """
        instances = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = instances.delete()
        return outcome

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

    @classmethod
    def get_unique_start_times(cls, school_id: int) -> List[dt.time]:
        """
        Method to find the unique period_start_at times for a givens school (ordered from first to last).
        Note that we are only interested in the times of day, and not the days.
        """
        slots = cls.objects.get_all_instances_for_school(school_id=school_id)
        times = slots.values_list("period_starts_at", flat=True)
        sorted_times = sorted(list(set(times)))  # Cannot use .distinct("period_starts_at") since SQLite doesn't support
        return sorted_times

    def check_if_slots_are_consecutive(self, other_slot: Self) -> bool:
        """
        Method to check if a slot is consecutive with the passed 'other_slot'
        """
        same_day = self.day_of_week == other_slot.day_of_week
        contiguous_time = ((self.period_starts_at == other_slot.period_ends_at) or
                           (self.period_ends_at == other_slot.period_starts_at))
        return same_day and contiguous_time

    # PROPERTIES
    @property
    def period_ends_at(self):
        """
        Property calculating the time at which a timetable slot ends.
        """
        end_datetime = dt.datetime.combine(date=dt.datetime.min, time=self.period_starts_at) + self.period_duration
        return end_datetime.time()
