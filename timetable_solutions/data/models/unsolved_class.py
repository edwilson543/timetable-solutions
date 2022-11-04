"""Module defining the model for a user-specified class requirements ('unsolved classes') and any ancillary objects."""

# Django imports
from django.core.exceptions import ValidationError
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.classroom import Classroom
from data.models.pupil import Pupil, PupilQuerySet
from data.models.teacher import Teacher


class UnsolvedClassQuerySet(models.QuerySet):
    """Custom queryset manager for the UnsolvedClass model"""

    def get_all_instances_for_school(self, school_id: int) -> models.QuerySet:
        """Method to return the full queryset of fixed classes for a given school"""
        return self.filter(school_id=school_id)

    def get_individual_unsolved_class(self, school_id: int, class_id: int):
        """Method to return an individual FixedClass instance"""
        return self.get(models.Q(school_id=school_id) & models.Q(class_id=class_id))


class UnsolvedClass(models.Model):
    """
    Model used to specify the school_id classes that must take place, including who must be able to attend them,
    and also teaching hours / min number of slots etc. "Unsolved" since it represents an input to the solver which
    finds the timetable structure that works across the board. Twin to "FixedClass" in view_timetables app.

    total_slots - total number of lessons per week, including any FixedClasses and double periods (which count as 2)
    n_double_periods - the number of double periods the unsolved class should be taught for, INCLUDING any FixedClass
    double periods. All count towards total_slots.
    """
    class_id = models.CharField(max_length=20)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=20)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT,
                                related_name="unsolved_classes", blank=True, null=True)
    pupils = models.ManyToManyField(Pupil, related_name="unsolved_classes")
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT,
                                  related_name="unsolved_classes", blank=True, null=True)
    total_slots = models.PositiveSmallIntegerField()
    n_double_periods = models.PositiveSmallIntegerField()

    # Introduce a custom manager
    objects = UnsolvedClassQuerySet.as_manager()

    class Constant:
        """
        Additional constants to store about the Teacher model (that aren't an option in Meta)
        """
        human_string_singular = "required class"
        human_string_plural = "required classes"

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"USC: {self.school}, {self.class_id}"

    def __repr__(self):
        """String representation of the model for debugging"""
        return f"USC: {self.school}, {self.class_id}"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, class_id: str, subject_name: str, teacher_id: int,
                   classroom_id: int, total_slots: int, n_double_periods: int, pupils: PupilQuerySet):
        """
        Method to create a new UnsolvedClass instance. Note that pupils are added separately since Pupil has a
        Many-to-many relationship with UnsolvedClasses, so the UnsolvedClass instance must first be saved.
        """
        subject_name = subject_name.upper()
        unsolved_cls = cls.objects.create(
            school_id=school_id, class_id=class_id, subject_name=subject_name, teacher_id=teacher_id,
            classroom_id=classroom_id, total_slots=total_slots, n_double_periods=n_double_periods)
        unsolved_cls.save()
        if len(pupils) > 0:
            unsolved_cls.pupils.add(*pupils)
        return unsolved_cls

    # MISCELLANEOUS METHODS
    def clean(self) -> None:
        """
        Additional validation on UnsolvedClass instances. In particular we cannot imply a number of double periods that
        would exceed the total number of slots.
        """
        if self.n_double_periods > (self.total_slots / 2):
            raise ValidationError(f"{self.__repr__} with only {self.total_slots} total slots cannot have "
                                  f"{self.n_double_periods} double periods.")
