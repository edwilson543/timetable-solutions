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
        return self.filter(school_id=school_id).order_by("year_group_id")

    def get_all_year_groups_with_pupils(self, school_id: int) -> "YearGroupQuerySet":
        """
        Method retrieving all YearGroups with at least one pupil.
        """
        all_ygs = self.get_all_instances_for_school(school_id=school_id)
        return all_ygs.annotate(n_pupils=models.Count("pupils")).filter(n_pupils__gt=0)

    def get_individual_year_group(
        self, school_id: int, year_group_id: int
    ) -> "YearGroup":
        """
        Method retrieving a specific YearGroup instance.
        """
        return self.get(
            models.Q(school_id=school_id) & models.Q(year_group_id=year_group_id)
        )

    def get_specific_year_groups(
        self, school_id: int, year_group_ids: frozenset[int]
    ) -> "YearGroupQuerySet":
        """
        Method retrieving a specific set of YearGroups.
        """
        return self.filter(
            models.Q(school_id=school_id) & models.Q(year_group_id__in=year_group_ids)
        )


class YearGroup(models.Model):
    """
    Database table for all year groups of all schools.
    For now, this model serves the purpose of being more of a 'TimetableGroup' - i.e. it is used to associate
    different year groups with different timetable structures.
    """

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    year_group_id = models.IntegerField()
    year_group_name = models.CharField(max_length=20)

    # Introduce a custom manager
    objects = YearGroupQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the YearGroup model
        """

        unique_together = [["school", "year_group_id"], ["school", "year_group_name"]]
        ordering = ["year_group_id"]

    class Constant:
        """
        Additional constants to store about the Year Group model (that aren't an option in Meta)
        """

        human_string_singular = "year group"
        human_string_plural = "year groups"

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        try:
            float(self.year_group_name)
            # If the year group can be interpreted as a number, it makes sense to say 'Year x'
            return f"Year {self.year_group_name}"
        except ValueError:
            # If not, we just want the year group name, e.g. 'Reception'
            return f"{self.year_group_name}"

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return self.__str__()

    # --------------------
    # Factories tests
    # --------------------

    @classmethod
    def create_new(
        cls, school_id: int, year_group_id: int, year_group_name: str
    ) -> "YearGroup":
        """
        Method to create a new YearGroup instance.
        """
        yg = cls.objects.create(
            school_id=school_id,
            year_group_id=year_group_id,
            year_group_name=year_group_name,
        )
        yg.full_clean()
        return yg

    @classmethod
    def delete_all_instances_for_school(cls, school_id: int) -> tuple:
        """Method deleting all entries for a school in the YearGroup table"""
        year_groups = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = year_groups.delete()
        return outcome

    # --------------------
    # Queries tests
    # --------------------

    def get_number_pupils(self) -> int:
        """Method querying for how many pupils there are in a year group"""
        return self.pupils.all().count()
