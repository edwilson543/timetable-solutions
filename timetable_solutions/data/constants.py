# Django imports
from django.db import models


class UserRole(models.IntegerChoices):
    """
    Choices for the different roles that users can have with respect to the site.
    """

    SCHOOL_ADMIN = 1, "Administrator"  # Only role with access to the custom admin site
    TEACHER = 2, "Teacher"
    PUPIL = 3, "Pupil"


class Day(models.IntegerChoices):
    """Choices for the different days of the week a lesson can take place at"""

    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"
    SATURDAY = 6, "Saturday"
    SUNDAY = 7, "Sunday"
