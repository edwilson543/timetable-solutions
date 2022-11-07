"""Module defining the model for a school_id in the database, and any ancillary objects"""

# Django imports
from django.db import models


class SchoolQuerySet(models.QuerySet):
    """Custom queryset manager for the School model"""
    def get_individual_school(self, school_id):
        """Method returning a specific School instance"""
        return self.get(school_access_key=school_id)


class School(models.Model):
    """
    Model representing a school_id, with every other model associated with one school_id instance via a foreign key
    """
    school_access_key = models.PositiveIntegerField(primary_key=True)
    school_name = models.CharField(max_length=50)

    # Introduce a custom manager
    objects = SchoolQuerySet.as_manager()

    def __str__(self):
        """String representation of the model for the django admin site"""
        return self.school_name

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_access_key: int, school_name: str):
        """Method to create a new School instance."""
        school = cls.objects.create(school_access_key=school_access_key, school_name=school_name)
        school.full_clean()
        return school

    # PROPERTIES
    @property
    def number_users(self) -> int:
        """Method to get the number of users associated with a school"""
        return self.profile_set.count()

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
    def has_unsolved_class_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded UnsolvedClass data into the database."""
        # noinspection PyUnresolvedReferences
        return self.unsolvedclass_set.exists()

    @property
    def has_user_defined_fixed_class_data(self) -> bool:
        """Indicates whether a user from the given school has uploaded FixedClass data into the database."""
        # noinspection PyUnresolvedReferences
        return self.fixedclass_set.filter(user_defined=True).exists()

    @property
    def has_timetable_solutions(self) -> bool:
        """Indicates whether any FixedClass data has been produced BY THE SOLVER and saved into the database."""
        # noinspection PyUnresolvedReferences
        return self.fixedclass_set.filter(user_defined=False).exists()
