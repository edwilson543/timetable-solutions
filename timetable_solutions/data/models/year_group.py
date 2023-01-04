"""
Module defining the model for a school year group, and any ancillary objects.
"""

# Django imports
from django.db import models

# Local application imports
from data.models.school import School


class YearGroupQuerySet(models.QuerySet):
    """
    Custom queryset manager for the YearGroup model.
    """

    def get_all_instances_for_school(self, school_id: int) -> "YearGroupQuerySet":
        """
        Method to retrieve all YearGroups associate with a school.
        """
        return self.filter(school_id=school_id)

    def get_individual_year_group(self, school_id: int, year_group: str) -> "YearGroup":
        """
        Method retrieving a specific YearGroup instance.
        """
        return self.get(models.Q(school_id=school_id) & models.Q(year_group=year_group))


class YearGroup(models.Model):
    """
    Database table for all year groups of all schools.
    For now, this model serves the purpose of being more of a 'TimetableGroup' - i.e. it is used to associate
    different year groups with different timetable structures.
    """

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    year_group = models.CharField(max_length=20)

    # Introduce a custom manager
    objects = YearGroupQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the YearGroup model
        """

        unique_together = [["school", "year_group"]]

    class Constant:
        """
        Additional constants to store about the Year Group model (that aren't an option in Meta)
        """

        human_string_singular = "year group"
        human_string_plural = "year groups"

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"Year {self.year_group}"

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return f"Year {self.year_group}"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, year_group: str | int) -> "YearGroup":
        """
        Method to create a new YearGroup instance.
        """
        yg = cls.objects.create(school_id=school_id, year_group=str(year_group))
        yg.full_clean()
        return yg

    @classmethod
    def delete_all_instances_for_school(cls, school_id: int) -> tuple:
        """Method deleting all entries for a school in the YearGroup table"""
        year_groups = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = year_groups.delete()
        return outcome
