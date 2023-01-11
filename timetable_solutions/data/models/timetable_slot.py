"""Module defining the model for a timetable slot and any ancillary objects."""

# Standard library imports
import datetime as dt
from functools import lru_cache

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.year_group import YearGroup, YearGroupQuerySet


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

    def get_all_instances_for_school(self, school_id: int) -> "TimetableSlotQuerySet":
        """Method returning the queryset of all timetable slots at the given school"""
        return self.filter(school_id=school_id)

    def get_individual_timeslot(self, school_id: int, slot_id: int) -> "TimetableSlot":
        """Method returning an individual Teacher"""
        return self.get(models.Q(school_id=school_id) & models.Q(slot_id=slot_id))

    def get_specific_timeslots(
        self, school_id: int, slot_ids: set[int]
    ) -> "TimetableSlotQuerySet":
        """Method returning the slots at the given school, with the corresponding slot_ids"""
        return self.filter(
            models.Q(school_id=school_id) & models.Q(slot_id__in=slot_ids)
        )

    def get_timeslots_on_given_day(
        self, school_id: int, day_of_week: WeekDay
    ) -> "TimetableSlotQuerySet":
        """Method returning the timetable slots for the school on the given day of the week"""
        return self.filter(
            models.Q(school_id=school_id) & models.Q(day_of_week=day_of_week)
        )


class TimetableSlot(models.Model):
    """Model for stating the unique timetable slots when classes can take place"""

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    slot_id = models.IntegerField()
    day_of_week = models.SmallIntegerField(choices=WeekDay.choices)
    period_starts_at = models.TimeField()
    period_duration = models.DurationField(default=dt.timedelta(hours=1))
    relevant_year_groups = models.ManyToManyField(YearGroup, related_name="slots")

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

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        day_of_week = WeekDay(self.day_of_week).label
        start_time = self.period_starts_at.strftime("%H:%M")
        return f"{day_of_week}, {start_time}"

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        day_of_week = WeekDay(self.day_of_week).label
        start_time = self.period_starts_at.strftime("%H:%M")
        return f"{day_of_week}, {start_time}"

    # FACTORIES
    @classmethod
    def create_new(
        cls,
        school_id: int,
        slot_id: int,
        day_of_week: WeekDay,
        period_starts_at: dt.time,
        period_duration: dt.timedelta,
        relevant_year_groups: YearGroupQuerySet | None = None,
    ) -> "TimetableSlot":
        """Method to create a new TimetableSlot instance."""
        try:
            day_of_week = WeekDay(day_of_week).value
        except ValueError:
            raise ValueError(
                f"Tried to create TimetableSlot instance with day_of_week: {day_of_week} of type: "
                f"{type(day_of_week)}"
            )

        slot = cls.objects.create(
            school_id=school_id,
            slot_id=slot_id,
            day_of_week=day_of_week,
            period_starts_at=period_starts_at,
            period_duration=period_duration,
        )
        slot.full_clean()

        if relevant_year_groups is not None:
            slot.add_year_groups(year_groups=relevant_year_groups)

        return slot

    @classmethod
    def delete_all_instances_for_school(cls, school_id: int) -> tuple:
        """
        Method to delete all the TimetableSlot instances associated with a particular school
        """
        instances = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = instances.delete()
        return outcome

    # MUTATORS
    def add_year_groups(self, year_groups: YearGroupQuerySet | YearGroup) -> None:
        """Method adding a queryset of / yeargroup instance to a TimetableSlot instance"""
        if isinstance(year_groups, YearGroupQuerySet):
            self.relevant_year_groups.add(*year_groups)
        elif isinstance(year_groups, YearGroup):
            self.relevant_year_groups.add(year_groups)

    # QUERIES
    @classmethod
    def get_timeslot_ids_on_given_day(
        cls, school_id: int, day_of_week: WeekDay
    ) -> list[int]:
        """
        Method returning the timetable slot IDs for the school on the given day of the week
        Method is cached since it's implicitly called form a list comp creating solver constraints on no repetition .
        """
        timeslots = cls.objects.get_timeslots_on_given_day(
            school_id=school_id, day_of_week=day_of_week
        )
        timeslot_ids = [timeslot.slot_id for timeslot in timeslots]
        return timeslot_ids

    @classmethod
    def get_unique_start_hours(cls, school_id: int) -> list[dt.time]:
        """
        Method to find the unique period_start_at times for a givens school (ordered from first to last).
        Note that we are only interested in the times of day, and not the days.
        """
        slots = cls.objects.get_all_instances_for_school(school_id=school_id)
        times = slots.values_list("period_starts_at", flat=True)
        unique_rounded_hours = {dt.time(hour=round(time.hour, 0)) for time in times}
        sorted_times = sorted(list(unique_rounded_hours))

        return sorted_times

    def check_if_slots_are_consecutive(self, other_slot: "TimetableSlot") -> bool:
        """
        Method to check if a slot is consecutive with the passed 'other_slot'
        """
        same_day = self.day_of_week == other_slot.day_of_week
        contiguous_time = (self.period_starts_at == other_slot.period_ends_at) or (
            self.period_ends_at == other_slot.period_starts_at
        )
        return same_day and contiguous_time

    # PROPERTIES
    @property
    def period_ends_at(self) -> dt.time:
        """
        Property calculating the time at which a timetable slot ends.
        """
        end_datetime = (
            dt.datetime.combine(date=dt.datetime.min, time=self.period_starts_at)
            + self.period_duration
        )
        return end_datetime.time()
