
# Standard library imports
import datetime as dt

# Django imports
from django.db import models


class Teacher(models.Model):
    """Model for storing unique list of teachers."""
    firstname = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)


class Pupil(models.Model):
    """Model for storing unique list of pupils."""

    class YearGroup(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5

    firstname = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    year_group = models.IntegerField(choices=YearGroup.choices)


class TimetableSlot(models.Model):
    """Model for stating the unique timetable slots when classes can take place"""

    class WeekDay(models.TextChoices):
        MONDAY = "MONDAY"
        TUESDAY = "TUESDAY"
        WEDNESDAY = "WEDNESDAY"
        THURSDAY = "THURSDAY"
        FRIDAY = "FRIDAY"

    class PeriodStart(dt.time, models.Choices):
        PERIOD_ONE = 9, 0, "PERIOD_ONE"
        PERIOD_TWO = 10, 0, "PERIOD_TWO"
        PERIOD_THREE = 11, 0, "PERIOD_THREE"
        PERIOD_FOUR = 12, 0, "PERIOD_FOUR"
        LUNCH = 13, 0, "LUNCH"
        PERIOD_FIVE = 14, 0, "PERIOD_FIVE"
        PERIOD_SIX = 15, 0, "PERIOD_SIX"

    day_of_week = models.CharField(max_length=9, choices=WeekDay.choices)
    period_start_time = models.TimeField(choices=PeriodStart.choices)
    period_duration = models.DurationField(default=dt.timedelta(hours=1))


class FixedClass(models.Model):
    """
    Model for storing the unique list of classes that take place, when they take place, the teacher that takes the
    class, and the pupils that attend the class.
    Note that teacher is nullable so that a FixedClass can be made for breaks.
    """
    class SubjectColour(models.TextChoices):
        """Enum to list the options and colour that each colour of the timetable should be."""
        MATHS = "#b3f2b3"
        ENGLISH = "#ffbfd6"
        FRENCH = "#c8d4e3"
        LUNCH = "#b3b3b3"
        FREE = "#feffba"

        @staticmethod
        def get_colour_from_subject(subject_name: str) -> str:
            return getattr(FixedClass.SubjectColour, subject_name).value

    class_id = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=20, choices=SubjectColour.choices)
    teacher = models.ForeignKey("Teacher", on_delete=models.PROTECT, related_name="classes", blank=True, null=True)
    pupils = models.ManyToManyField("Pupil", related_name="classes")
    time_slots = models.ManyToManyField("TimetableSlot", related_name="classes")
