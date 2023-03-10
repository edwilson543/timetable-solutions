"""Module defining the model for a school_id in the database, and any ancillary objects"""


# Django imports
from django.db import models


class SchoolQuerySet(models.QuerySet):
    """Custom queryset manager for the School model"""

    def get_individual_school(self, school_id: int) -> "School":
        """Method returning a specific School instance"""
        return self.get(school_access_key=school_id)


class School(models.Model):
    """
    Model representing a school_id, with every other model associated with one school_id instance via a foreign key
    """

    school_access_key = models.AutoField(primary_key=True)
    school_name = models.CharField(max_length=50)

    # Introduce a custom manager
    objects = SchoolQuerySet.as_manager()

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return str(self.school_name)

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return str(self.school_name)

    # --------------------
    # Factories tests
    # --------------------

    @classmethod
    def create_new(cls, school_name: str) -> "School":
        """
        Method to create a new School instance. If no access key is given, then one is generated.
        """
        school = cls.objects.create(school_name=school_name)
        school.full_clean()
        return school

    # --------------------
    # Properties tests
    # --------------------

    @property
    def number_users(self) -> int:
        """Method to get the number of users associated with a school"""
        # noinspection PyUnresolvedReferences
        return self.profile_set.count()

    @property
    def has_year_group_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded YearGroup data into the database."""
        # noinspection PyUnresolvedReferences
        return self.yeargroup_set.exists()

    @property
    def has_teacher_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded Teacher data into the database."""
        # noinspection PyUnresolvedReferences
        return self.teacher_set.exists()

    @property
    def has_pupil_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded Pupil data into the database."""
        # noinspection PyUnresolvedReferences
        return self.pupil_set.exists()

    @property
    def has_classroom_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded Classroom data into the database."""
        # noinspection PyUnresolvedReferences
        return self.classroom_set.exists()

    @property
    def has_timetable_structure_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded TimetableSlot data into the database."""
        # noinspection PyUnresolvedReferences
        return self.timetableslot_set.exists()

    @property
    def has_lesson_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded Lesson data into the database."""
        # noinspection PyUnresolvedReferences
        return self.lesson_set.exists()

    @property
    def has_break_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded Break data into the database."""
        # noinspection PyUnresolvedReferences
        return self.break_set.exists()
