"""Module defining the model for a timetable slot and any ancillary objects."""


# Standard library imports
import datetime as dt
from typing import TYPE_CHECKING

# Django imports
from django.db import models

# Local application imports
from data import constants
from data.models.school import School
from data.models.year_group import YearGroup, YearGroupQuerySet

if TYPE_CHECKING:
    # Local application imports
    from data.models import lesson


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
        self, school_id: int, day_of_week: constants.Day, year_group: YearGroup
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


class TimetableSlot(models.Model):
    """Model for stating the unique timetable slots when classes can take place"""

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    slot_id = models.IntegerField()
    day_of_week = models.SmallIntegerField(choices=constants.Day.choices)
    starts_at: dt.time = models.TimeField()
    ends_at: dt.time = models.TimeField()
    relevant_year_groups = models.ManyToManyField(YearGroup, related_name="slots")

    # Introduce a custom manager
    objects = TimetableSlotQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the TimetableSlot model
        """

        constraints = [
            models.UniqueConstraint(
                "school", "slot_id", name="slot_id_unique_for_school"
            ),
            models.CheckConstraint(
                check=models.Q(starts_at__lt=models.F("ends_at")),
                name="slot_ends_after_it_starts",
            ),
        ]
        ordering = ["day_of_week", "starts_at"]

    class Constant:
        """
        Additional constants to store about the TimetableSlot model (that aren't an option in Meta)
        """

        human_string_singular = "timetable slot"
        human_string_plural = "timetable slots"

        # Field names
        relevant_year_groups = "relevant_year_groups"

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        day_of_week = constants.Day(self.day_of_week).label
        start_time = self.starts_at.strftime("%H:%M")
        return f"{day_of_week}, {start_time}"

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        day_of_week = constants.Day(self.day_of_week).label
        start_time = self.starts_at.strftime("%H:%M")
        return f"{day_of_week}, {start_time}"

    # --------------------
    # Factories
    # --------------------

    @classmethod
    def create_new(
        cls,
        school_id: int,
        slot_id: int,
        day_of_week: constants.Day,
        starts_at: dt.time,
        ends_at: dt.time,
        relevant_year_groups: YearGroupQuerySet | None = None,
    ) -> "TimetableSlot":
        """
        Create a new TimetableSlot instance.
        """
        slot = cls.objects.create(
            school_id=school_id,
            slot_id=slot_id,
            day_of_week=day_of_week,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        if relevant_year_groups:
            slot._add_year_groups(year_groups=relevant_year_groups)
        slot.full_clean()
        return slot

    @classmethod
    def delete_all_instances_for_school(cls, school_id: int) -> tuple:
        """
        Method to delete all the TimetableSlot instances associated with a particular school
        """
        instances = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = instances.delete()
        return outcome

    # --------------------
    # Mutators
    # --------------------

    def update_slot_timings(
        self,
        *,
        day_of_week: constants.Day | None = None,
        starts_at: dt.time | None = None,
        ends_at: dt.time | None = None,
    ) -> "TimetableSlot":
        """
        Update the time of day that this slot occurs at.
        """
        self.day_of_week = day_of_week or self.day_of_week
        self.starts_at = starts_at or self.starts_at
        self.ends_at = ends_at or self.ends_at
        self.save(update_fields=["day_of_week", "starts_at", "ends_at"])
        return self

    def update_relevant_year_groups(
        self,
        relevant_year_groups: YearGroupQuerySet,
    ) -> "TimetableSlot":
        """
        Update the year groups that are relevant to this slot.
        """
        self.relevant_year_groups.set(relevant_year_groups)
        return self

    def _add_year_groups(self, year_groups: YearGroupQuerySet | YearGroup) -> None:
        """
        Add a queryset of yeargroups to a TimetableSlot instance.
        """
        self.relevant_year_groups.add(*year_groups)

    # --------------------
    # Queries
    # --------------------

    @classmethod
    def get_timeslot_ids_on_given_day(
        cls, school_id: int, day_of_week: constants.Day, year_group: YearGroup
    ) -> list[int]:
        """
        Method returning the timetable slot IDs for the school on the given day of the week
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
        times = slots.values_list("starts_at", flat=True)
        unique_rounded_hours = {dt.time(hour=round(time.hour, 0)) for time in times}
        sorted_times = sorted(list(unique_rounded_hours))

        return sorted_times

    def get_all_lessons(self) -> "lesson.LessonQuerySet":
        """
        Get all the lessons this slot is in use for
        """
        return self.user_lessons.all() | self.solver_lessons.all()

    def check_if_slots_are_consecutive(self, other_slot: "TimetableSlot") -> bool:
        """
        Method to check if a slot is consecutive with the passed 'other_slot'
        """
        same_day = self.day_of_week == other_slot.day_of_week
        contiguous_time = (self.starts_at == other_slot.ends_at) or (
            self.ends_at == other_slot.starts_at
        )
        return same_day and contiguous_time

    # --------------------
    # Properties
    # --------------------

    @property
    def open_interval(self) -> tuple[dt.time, dt.time]:
        """
        Duration which the slot covers +/- a second (a 'fake' open interval really).
        This is so that comparing with another slot doesn't give undesired clashes.
        """
        one_second = dt.timedelta(seconds=1)

        open_start_time = (
            dt.datetime.combine(date=dt.datetime.min, time=self.starts_at) + one_second
        ).time()

        open_end_time = (
            dt.datetime.combine(date=dt.datetime.min, time=self.ends_at) - one_second
        ).time()

        return open_start_time, open_end_time
