from django.db import models

from data.models import School
from data.models.classroom import Classroom
from data.models.fixed_class import FixedClass
from data.models.pupil import Pupil
from data.models.teacher import Teacher


class UnsolvedClass(models.Model):
    """
    Model used to specify the school classes that must take place, including who must be able to attend them,
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
    min_slots = models.PositiveSmallIntegerField()