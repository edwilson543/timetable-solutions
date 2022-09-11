"""Core models of the timetable project - these models are used across the django apps."""

# Standard library imports
import datetime as dt

# Django imports
from django.db import models

# Local application imports
from users.models import School


class Teacher(models.Model):
    """
    Model for storing a unique list of teachers.
    Note that the teacher_id is NOT set as a manual primary key since users will need to use this when uploading
    their own data, and certain primary keys may already be taken in the database by other schools.
    """
    teacher_id = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    title = models.CharField(max_length=10)


class Pupil(models.Model):
    """Model for storing unique list of pupils."""

    class YearGroup(models.IntegerChoices):
        ONE = 1, "#b3f2b3"
        TWO = 2, "#ffbfd6"
        THREE = 3, "#c8d4e3"
        FOUR = 4, "#fcc4a2"
        FIVE = 5, "#babac2"

        @staticmethod
        def get_colour_from_year_group(year_group: int) -> str:
            """Method taking a year group name e.g. int: 1 and returning a hexadecimal colour e.g. #b3f2b3"""
            member = Pupil.YearGroup(year_group)
            return member.label

    pupil_id = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
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

    slot_id = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=9, choices=WeekDay.choices)
    period_start_time = models.TimeField(choices=PeriodStart.choices)
    period_duration = models.DurationField(default=dt.timedelta(hours=1))


class Classroom(models.Model):
    """
    Model storing the classroom (location) in which a fixed class takes place.
    Currently, a fixed class id must take place in exactly one classroom
    """
    classroom_id = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    building = models.CharField(max_length=20)
    room_number = models.IntegerField()


class FixedClass(models.Model):
    """
    Model for storing the unique list of classes that take place, when they take place, the teacher that takes the
    class, and the pupils that attend the class.
    Note that teacher is nullable so that a FixedClass can be made for breaks.
    """
    class SubjectColour(models.TextChoices):
        """Enum to list the options and colour that each colour of the timetable should be."""
        MATHS = "MATHS", "#b3f2b3"
        ENGLISH = "ENGLISH", "#ffbfd6"
        FRENCH = "FRENCH", "#c8d4e3"
        LUNCH = "LUNCH", "#b3b3b3"
        FREE = "FREE", "#feffba"

        @staticmethod
        def get_colour_from_subject(subject_name: str) -> str:
            """Method taking a subject name e.g. 'MATHS' and returning a hexadecimal colour e.g. #b3f2b3"""
            return getattr(FixedClass.SubjectColour, subject_name).label

    class_id = models.CharField(max_length=20)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=20, choices=SubjectColour.choices)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="classes", blank=True, null=True)
    pupils = models.ManyToManyField(Pupil, related_name="classes")
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="classes", blank=True, null=True)
    time_slots = models.ManyToManyField(TimetableSlot, related_name="classes")
    user_defined = models.BooleanField()  # If True, this is a class user has said must occur at a certain time
