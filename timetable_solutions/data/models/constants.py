from django.db import models


class WeekDay(models.IntegerChoices):
    """Choices for the different days of the week a lesson can take place at"""

    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"
