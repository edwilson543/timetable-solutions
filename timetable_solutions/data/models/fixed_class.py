"""Module defining the model for a 'FixedClass' (i.e. a class with solved timetable slots) and any ancillary objects."""

# Standard library imports
from typing import Optional

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.classroom import Classroom
from data.models.pupil import Pupil, PupilQuerySet
from data.models.teacher import Teacher
from data.models.timetable_slot import TimetableSlot, TimetableSlotQuerySet


class FixedClassQuerySet(models.QuerySet):
    """Custom queryset manager for the FixedClass model"""

    def get_all_instances_for_school(self, school_id: int) -> models.QuerySet:
        """Method to return the full queryset of fixed classes for a given school"""
        return self.filter(school_id=school_id)

    def get_individual_fixed_class(self, school_id: int, class_id: int):
        """Method to return an individual FixedClass instance"""
        return self.get(models.Q(school_id=school_id) & models.Q(class_id=class_id))

    def get_non_user_defined_fixed_classes(self, school_id: int) -> models.QuerySet:
        """Method returning the queryset of FixedClass instances created by the solver"""
        return self.filter(models.Q(school_id=school_id) & models.Q(user_defined=False))


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

    # Introduce a custom manager
    objects = FixedClassQuerySet.as_manager()

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.class_id} (fixed)"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, class_id: str, subject_name: str, user_defined: bool,
                   pupils: PupilQuerySet, time_slots: TimetableSlotQuerySet,
                   teacher_id: Optional[int] = None, classroom_id: Optional[int] = None):
        """
        Method to create a new FixedClass instance. Note that pupils and timetable slots get added separately,
        since they have a many to many relationship to the FixedClass model, so the fixed class must be saved first.
        """
        fixed_cls = cls.objects.create(
            school_id=school_id, class_id=class_id, subject_name=subject_name, teacher_id=teacher_id,
            classroom_id=classroom_id, user_defined=user_defined)
        fixed_cls.save()

        fixed_cls.add_pupils(pupils=pupils)
        fixed_cls.add_time_slots(time_slots=time_slots)

        return fixed_cls

    # MUTATORS
    def add_pupils(self, pupils: PupilQuerySet) -> None:
        """Method adding adding a queryset of pupils to the FixedClass instance's many-to-many pupils field"""
        self.pupils.add(*pupils)

    def add_time_slots(self, time_slots: TimetableSlotQuerySet) -> None:
        """Method adding adding a queryset of time slots to the FixedClass instance's many-to-many time_slot field"""
        self.time_slots.add(*time_slots)

    # PROPERTIES
    @property
    def number_slots_per_week(self) -> int:
        """Method to get the number of TimetableSlot instances associated with a given FixedClass"""
        return self.time_slots.count()
