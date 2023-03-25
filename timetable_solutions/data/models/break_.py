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
from data.models.year_group import YearGroup, YearGroupQuerySet


class BreakQuerySet(models.QuerySet):
    """
    Custom queryset manager for the Break. model
    """

    def get_all_instances_for_school(self, school_id: int) -> "BreakQuerySet":
        """
        Get all breaks for a given school.
        """
        return self.filter(school_id=school_id)

    def get_all_instances_for_school_with_year_groups(
        self, school_id: int
    ) -> "BreakQuerySet":
        """
        Get a school's breaks that have at least one year group.
        """
        return self.annotate(
            n_relevant_year_groups=models.Count("relevant_year_groups")
        ).filter(models.Q(school_id=school_id) & models.Q(n_relevant_year_groups__gt=0))


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
        teachers: TeacherQuerySet | None,
        relevant_year_groups: YearGroupQuerySet | None,
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

        if teachers:
            break_._add_teachers(teachers)
        if relevant_year_groups:
            break_._add_year_groups(relevant_year_groups)

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

    def update_break_timings(
        self,
        *,
        break_name: str = "",
        day_of_week: constants.Day | None = None,
        starts_at: dt.time | None = None,
        ends_at: dt.time | None = None,
    ) -> "Break":
        """
        Update the time of day that this slot occurs at.
        """
        self.break_name = break_name or self.break_name
        self.day_of_week = day_of_week or self.day_of_week
        self.starts_at = starts_at or self.starts_at
        self.ends_at = ends_at or self.ends_at
        self.save(update_fields=["break_name", "day_of_week", "starts_at", "ends_at"])
        return self

    def update_relevant_year_groups(
        self,
        relevant_year_groups: YearGroupQuerySet,
    ) -> "Break":
        """
        Update the year groups that are relevant to this slot.
        """
        self.relevant_year_groups.set(relevant_year_groups)
        return self

    def _add_teachers(self, teachers: TeacherQuerySet | Teacher) -> None:
        """
        Add one or more teachers to a break instance.
        """
        self.teachers.add(*teachers)

    def _add_year_groups(self, year_groups: YearGroupQuerySet | YearGroup) -> None:
        """
        Add one or more year groups to a break instance.
        """
        self.relevant_year_groups.add(*year_groups)
