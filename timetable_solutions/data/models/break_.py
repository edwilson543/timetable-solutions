"""
Module defining the model for a SchoolClass, and its manager.
"""


# Standard library imports
import datetime as dt

# Django imports
from django.db import models

# Local application imports
from data import constants
from data.models.school import School
from data.models.teacher import Teacher, TeacherQuerySet
from data.models.timetable_slot import TimetableSlot
from data.models.year_group import YearGroup, YearGroupQuerySet


class BreakQuerySet(models.QuerySet):
    """
    Custom queryset manager for the Break. model
    """

    def get_all_instances_for_school(self, school_id: int) -> "BreakQuerySet":
        """Method to return the full queryset of lessons for a given school"""
        return self.filter(school_id=school_id)

    # --------------------
    # Filters
    # --------------------

    def filter_for_clashes(self, slot: TimetableSlot) -> bool:
        """
        Filter a queryset of breaks against an individual TimetableSlot.
        :return The breaks in the queryset (self) that clash with the passed slot, non-inclusively.

        See also filter_for_clashes on TimetableSlot.
        """
        clash_interval = slot.open_interval

        clashes = self.filter(
            (
                (
                    # OVERLAPPING clashes
                    models.Q(starts_at__range=clash_interval)
                    | models.Q(ends_at__range=clash_interval)
                )
                | (
                    # EXACT MATCH clashes
                    # We do however want slots to clash with themselves / other slots starting and finishing
                    # at the same time, since a user may have defined slots covering the same time pan
                    models.Q(starts_at=slot.starts_at)
                    | models.Q(ends_at=slot.ends_at)
                )
            )
            & models.Q(day_of_week=slot.day_of_week)
        )
        return clashes


class Break(models.Model):
    """
    Model representing a break in the school day.
    """

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    break_id = models.CharField(max_length=20)
    break_name = models.CharField(max_length=20)

    day_of_week = models.SmallIntegerField(choices=constants.Day.choices)
    starts_at: dt.time = models.TimeField()
    ends_at: dt.time = models.TimeField()

    teachers = models.ManyToManyField(Teacher, related_name="breaks")
    relevant_year_groups = models.ManyToManyField(YearGroup, related_name="breaks")

    # Introduce a custom manager
    objects = BreakQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the Break model
        """

        constraints = [
            models.UniqueConstraint(
                "school", "break_id", name="break_id_unique_for_school"
            ),
            models.CheckConstraint(
                check=models.Q(starts_at__lt=models.F("ends_at")),
                name="break_ends_after_it_starts",
            ),
        ]

        unique_together = [["school", "break_id"]]

    class Constant:
        """
        Additional constants to store about the Lesson model (that aren't an option in Meta)
        """

        human_string_singular = "break"
        human_string_plural = "breaks"

        # M2M field names
        teachers = "teachers"
        relevant_year_groups = "relevant_year_groups"

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"{self.break_id}".title().replace("_", " ")

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return f"{self.school}: {self.break_id}"

    # --------------------
    # Factories
    # --------------------

    @classmethod
    def create_new(
        cls,
        school_id: int,
        break_id: str,
        break_name: str,
        day_of_week: constants.Day,
        starts_at: dt.time,
        ends_at: dt.time,
        teachers: TeacherQuerySet,
        relevant_year_groups: YearGroupQuerySet,
    ) -> "Break":
        """
        Method for creating a new Break instance in the db.
        """
        break_ = cls.objects.create(
            school_id=school_id,
            break_id=break_id,
            break_name=break_name,
            starts_at=starts_at,
            ends_at=ends_at,
            day_of_week=day_of_week,
        )
        break_.full_clean()

        break_.add_teachers(teachers)
        break_.add_year_groups(relevant_year_groups)

        return break_

    @classmethod
    def delete_all_breaks_for_school(cls, school_id: int) -> tuple:
        """Method deleting all entries for a school in the Break table"""
        breaks = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = breaks.delete()
        return outcome

    # --------------------
    # Mutators
    # --------------------

    def add_teachers(self, teachers: TeacherQuerySet | Teacher) -> None:
        """
        Add one or more teachers to a break instance.
        """
        if isinstance(teachers, TeacherQuerySet):
            self.teachers.add(*teachers)
        elif isinstance(teachers, Teacher):
            self.teachers.add(teachers)

    def add_year_groups(self, year_groups: YearGroupQuerySet | YearGroup) -> None:
        """
        Add one or more year groups to a break instance.
        """
        if isinstance(year_groups, YearGroupQuerySet):
            self.relevant_year_groups.add(*year_groups)
        elif isinstance(year_groups, YearGroup):
            self.relevant_year_groups.add(year_groups)
