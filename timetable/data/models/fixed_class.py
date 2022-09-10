"""Module defining the model for a 'FixedClass' (i.e. a class with solved timetable slots) and any ancillary objects."""

# Standard library imports
from typing import Set

# Django imports
from django.core.exceptions import ObjectDoesNotExist
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
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT, related_name="classes", blank=True, null=True)
    pupils = models.ManyToManyField(Pupil, related_name="classes")
    time_slots = models.ManyToManyField(TimetableSlot, related_name="classes")
    user_defined = models.BooleanField()  # If True, this is a class user has said must occur at a certain time

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.class_id} (fixed)"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, class_id: str, subject_name: str, user_defined: bool,
                   teacher_id: int | None = None, classroom_id: int | None = None):
        """
        Method to create a new FixedClass instance. Note that pupils and timetable slots get added separately,
        since they have a many to many relationship to the FixedClass model.
        """
        fixed_cls = cls.objects.create(
            school_id=school_id, class_id=class_id, subject_name=subject_name, teacher_id=teacher_id,
            classroom_id=classroom_id, user_defined=user_defined)
        return fixed_cls

    # MUTATION METHODS
    def add_pupils(self, pupil_ids: Set[int]) -> None:
        """
        Method to associate a set of pupils with an individual fixed class
        :param pupil_ids - a set of primary keys relating to pupils, with the fixed class to become associate with each
        """
        # noinspection PyUnresolvedReferences
        self.pupils.add(*pupil_ids)
        self.save()

    def add_timetable_slots(self, slot_ids: Set[int]) -> None:
        """
        Method to associate a set of timetable slots with an individual FixedClass
        :param slot_ids - a set of primary keys relating to timetable slots to associate this fixed class instance with
        """
        # noinspection PyUnresolvedReferences
        self.time_slots.add(*slot_ids)
        self.save()
