"""Module defining the model for a 'FixedClass' (i.e. a class with solved timetable slots) and any ancillary objects."""

# Standard library imports
from typing import Optional, Union, Tuple

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.classroom import Classroom
from data.models.pupil import Pupil, PupilQuerySet
from data.models.teacher import Teacher
from data.models.timetable_slot import TimetableSlot, TimetableSlotQuerySet, WeekDay


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

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    class_id = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=20)
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

    # FACTORIES
    @classmethod
    def create_new(cls, school_id: int, class_id: str, subject_name: str, user_defined: bool,
                   pupils: PupilQuerySet, time_slots: TimetableSlotQuerySet,
                   teacher_id: Optional[int] = None, classroom_id: Optional[int] = None):
        """
        Method to create a new FixedClass instance. Note that pupils and timetable slots get added separately,
        since they have a many to many relationship to the FixedClass model, so the fixed class must be saved first.
        """
        subject_name = subject_name.upper()
        fixed_cls = cls.objects.create(
            school_id=school_id, class_id=class_id, subject_name=subject_name, teacher_id=teacher_id,
            classroom_id=classroom_id, user_defined=user_defined)
        fixed_cls.save()

        if len(pupils) > 0:
            fixed_cls.add_pupils(pupils=pupils)
        if len(time_slots) > 0:
            fixed_cls.add_time_slots(time_slots=time_slots)

        return fixed_cls

    @classmethod
    def delete_all_non_user_defined_fixed_classes(cls, school_id: int, return_info: bool = False) -> Union[Tuple, None]:
        """Method deleting the queryset of FixedClass instances previously produced by the solver"""
        fcs = cls.objects.get_non_user_defined_fixed_classes(school_id=school_id)
        info = fcs.delete()
        if return_info:
            return info

    # MUTATORS
    def add_pupils(self, pupils: PupilQuerySet) -> None:
        """Method adding adding a queryset of pupils to the FixedClass instance's many-to-many pupils field"""
        self.pupils.add(*pupils)

    def add_time_slots(self, time_slots: TimetableSlotQuerySet) -> None:
        """Method adding adding a queryset of time slots to the FixedClass instance's many-to-many time_slot field"""
        self.time_slots.add(*time_slots)

    # QUERIES
    def get_double_period_count_on_day(self, day_of_week: WeekDay) -> int:
        """
        Method to count the number of user-defined double periods on the given day
        To achieve this, we iterate through the full set of ordered TimeTable Slot
        :return - an integer specifying how many double periods the FixedClass instance has on the given day
        """
        if not self.user_defined:
            raise ValueError(f"get_double_period_count_on_day was called for a non-user defined class!")

        else:
            # Note that slots will be ordered in time, using the TimetableSlot Meta class
            fixed_class_slots = self.time_slots.all().get_timeslots_on_given_day(
                school_id=self.school.school_access_key, day_of_week=day_of_week)
            all_timetable_slots = TimetableSlot.objects.get_timeslots_on_given_day(
                school_id=self.school.school_access_key, day_of_week=day_of_week)

            # Set initial parameters affected by the for loop
            double_period_count = 0
            active_day = None
            had_previous_slot = False

            # We compare the full list of ORDERED timetable slots on the given day, with the slots on the FixedClass
            for current_slot in all_timetable_slots:

                # First we check that we haven't changed day of the week, which would prevent a double
                if active_day != current_slot.day_of_week:
                    active_day = current_slot.day_of_week
                    if current_slot in fixed_class_slots:
                        had_previous_slot = True  # We still need to acknowledge that the FC has the current slot
                    continue
                else:
                    active_day = current_slot.day_of_week

                # Next we check whether the FixedClass has both the current slot and the previous slot attached
                if current_slot in fixed_class_slots:
                    if had_previous_slot:  # FixedClass has the previous slot and next slot, so has a double
                        double_period_count += 1
                    had_previous_slot = True
                else:
                    had_previous_slot = False

            return double_period_count

    def number_slots_per_week(self) -> int:
        """Method to get the number of TimetableSlot instances associated with a given FixedClass"""
        return self.time_slots.all().count()
