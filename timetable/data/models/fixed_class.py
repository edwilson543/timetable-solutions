from django.db import models

# Create your models here.
from data.models import School
from data.models.classroom import Classroom
from data.models.pupil import Pupil
from data.models.teacher import Teacher
from data.models.timetable_slot import TimetableSlot


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