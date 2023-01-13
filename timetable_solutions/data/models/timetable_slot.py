"""Module defining the model for a timetable slot and any ancillary objects."""

# Standard library imports
import datetime as dt

# Django imports
from django.core import exceptions
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
        self, school_id: int, day_of_week: WeekDay, year_group: YearGroup
    ) -> "TimetableSlotQuerySet":
        """
        Method returning the timetable slots for the school on the given day of the week,
        relevant to a particular year group.
        """
        return self.filter(
            models.Q(school_id=school_id)
            & models.Q(day_of_week=day_of_week)
            & models.Q(relevant_year_groups=year_group)
        )

    # Filters

    def filter_for_clashes(self, slot: "TimetableSlot") -> "TimetableSlotQuerySet":
        """
        Filter a queryset of slots against an individual slot.
        :return The slots in the queryset (self) that clash with the passed slot, non-inclusively.

        The use case for this is to check whether teachers / classrooms / (pupil) are busy at a give slot,
        at any point during that slot.
        """
        clash_range = slot.open_interval
        # Note the django __range filter is inclusive, hence the open interval is essential,
        # otherwise we just get slots that start/finish at the same time e.g. 9-10, 10-11...

        return self.filter(
            (
                (
                    # OVERLAPPING clashes
                    models.Q(period_starts_at__range=clash_range)
                    | models.Q(period_ends_at__range=clash_range)
                )
                | (
                    # EXACT MATCH clashes
                    # We do however want slots to clash with themselves / other slots starting and finishing
                    # at the same time, since a user may have defined slots covering the same time pan
                    models.Q(period_starts_at=slot.period_starts_at)
                    | models.Q(period_ends_at=slot.period_ends_at)
                )
            )
            & models.Q(day_of_week=slot.day_of_week)
        )


class TimetableSlot(models.Model):
    """Model for stating the unique timetable slots when classes can take place"""

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    slot_id = models.IntegerField()
    day_of_week = models.SmallIntegerField(choices=WeekDay.choices)
    period_starts_at: dt.time = models.TimeField()
    period_ends_at: dt.time = models.TimeField()
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
        period_ends_at: dt.time,
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
            period_ends_at=period_ends_at,
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
        cls, school_id: int, day_of_week: WeekDay, year_group: YearGroup
    ) -> list[int]:
        """
        Method returning the timetable slot IDs for the school on the given day of the week
        Method is cached since it's implicitly called form a list comp creating solver constraints on no repetition .
        """
        timeslots = cls.objects.get_timeslots_on_given_day(
            school_id=school_id, day_of_week=day_of_week, year_group=year_group
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
    def period_duration(self) -> dt.timedelta:
        """
        Property calculating the time at which a timetable slot ends.
        """
        start = dt.datetime.combine(date=dt.datetime.min, time=self.period_starts_at)
        end = dt.datetime.combine(date=dt.datetime.min, time=self.period_ends_at)
        dur = end - start
        return dur

    @property
    def open_interval(self) -> tuple[dt.time, dt.time]:
        """
        Duration which the slot covers +/- a second (a 'fake' open interval really).
        This is so that comparing with another slot doesn't give undesired clashes.
        """
        one_second = dt.timedelta(seconds=1)

        open_start_time = (
            dt.datetime.combine(date=dt.datetime.min, time=self.period_starts_at)
            + one_second
        ).time()

        open_end_time = (
            dt.datetime.combine(date=dt.datetime.min, time=self.period_ends_at)
            - one_second
        ).time()

        return open_start_time, open_end_time

    # Checks
    def clean(self) -> None:
        """
        Additional validation on TimetablesLOT instances.
        """
        if self.period_ends_at <= self.period_starts_at:
            raise exceptions.ValidationError(
                "Period cannot finish before it has started!"
            )
