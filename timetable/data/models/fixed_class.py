"""Module defining the model for a 'FixedClass' (i.e. a class with solved timetable slots) and any ancillary objects."""

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.classroom import Classroom
from data.models.pupil import Pupil
from data.models.teacher import Teacher
from data.models.timetable_slot import TimetableSlot


class FixedClass(models.Model):
    """
    Model storing the classes that take place, when they take place, the teacher that takes the class, and the pupils
    that attend the class.
    Note that teacher is nullable so that a FixedClass can be made for breaks e.g. lunch time.
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

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    class_id = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=20, choices=SubjectColour.choices)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="classes", blank=True, null=True)
    pupils = models.ManyToManyField(Pupil, related_name="classes")
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="classes", blank=True, null=True)
    time_slots = models.ManyToManyField(TimetableSlot, related_name="classes")
    user_defined = models.BooleanField()  # If True, this is a class user has said must occur at a certain time

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.class_id} (fixed)"
