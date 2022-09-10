"""Module defining the model for a user-specified class requirements ('unsolved classes') and any ancillary objects."""

# Standard library imports
from typing import List

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.classroom import Classroom
from data.models.fixed_class import FixedClass
from data.models.pupil import Pupil
from data.models.teacher import Teacher


class UnsolvedClass(models.Model):
    """
    Model used to specify the school_id classes that must take place, including who must be able to attend them,
    and also teaching hours / min number of slots etc. "Unsolved" since it represents an input to the solver which
    finds the timetable structure that works across the board. Twin to "FixedClass" in timetable_selector app.
    """
    class_id = models.CharField(max_length=20, primary_key=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=20, choices=FixedClass.SubjectColour.choices)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT,
                                related_name="unsolved_classes", blank=True, null=True)
    pupils = models.ManyToManyField(Pupil, related_name="unsolved_classes")
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT,
                                  related_name="unsolved_classes", blank=True, null=True)
    total_slots = models.PositiveSmallIntegerField()
    min_distinct_slots = models.PositiveSmallIntegerField()

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.class_id} (unsolved)"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, class_id: str, subject_name: str, teacher_id: int,
                   classroom_id: int, total_slots: int, min_distinct_slots: int):
        """
        Method to create a new UnsolvedClass instance. Note that pupils are added separately since Pupil has a
        Many-to-many relationship with UnsolvedClasses.
        """
        unsolved_cls = cls.objects.create(school_id=school_id, class_id=class_id, subject_name=subject_name,
                                          teacher_id=teacher_id, classroom_id=classroom_id, total_slots=total_slots,
                                          min_distinct_slots=min_distinct_slots)
        return unsolved_cls

    # MUTATION METHODS
    def add_pupils(self):
        # TODO
        pass
