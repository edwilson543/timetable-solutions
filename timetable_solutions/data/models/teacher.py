"""Module defining the model for a teacher and any ancillary objects."""

# Django imports
from django.db import models

# Local application imports (other models)
from data.models.school import School
from data.models.timetable_slot import TimetableSlot


class TeacherQuerySet(models.QuerySet):
    """Custom queryset manager for the Teacher model"""

    def get_all_instances_for_school(self, school_id: int) -> models.QuerySet:
        """Method returning the queryset of teachers registered at the given school"""
        return self.filter(school_id=school_id)

    def get_individual_teacher(self, school_id: int, teacher_id: int):
        """Method returning an individual Teacher"""
        return self.get(models.Q(school_id=school_id) & models.Q(teacher_id=teacher_id))

    def get_teachers_surnames_starting_with_x(self, school_id: int, letter: str):
        """Method returning the queryset of Teacher instances whose surname starts with the letter x."""
        query_set = self.filter(models.Q(school_id=school_id) & models.Q(surname__startswith=letter))
        query_set.order_by("firstname")
        return query_set


class Teacher(models.Model):
    """
    Model for storing a unique list of teachers.
    Note that the teacher_id is NOT set as a manual primary key since users will need to use this when uploading
    their own data, and certain primary keys may already be taken in the database by other schools.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    teacher_id = models.IntegerField()
    firstname = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    title = models.CharField(max_length=10)

    # Introduce a custom manager
    objects = TeacherQuerySet.as_manager()

    class Constant:
        """
        Additional constants to store about the Teacher model (that aren't an option in Meta)
        """
        human_string_singular = "teacher"
        human_string_plural = "teachers"

    def __str__(self):
        """String representation of the model for the django admin site"""
        return f"{self.school}: {self.title} {self.surname}, {self.firstname}"

    def __repr__(self):
        """String representation of the model for debugging"""
        return f"Teacher {self.school}: {self.teacher_id}"

    # FACTORY METHODS
    @classmethod
    def create_new(cls, school_id: int, teacher_id: int, firstname: str, surname: str, title: str):
        """Method to create a new Teacher instance."""
        teacher = cls.objects.create(school_id=school_id, teacher_id=teacher_id, firstname=firstname, surname=surname,
                                     title=title)
        teacher.full_clean()
        return teacher

    # FILTER METHODS
    def check_if_busy_at_time_slot(self, slot: TimetableSlot) -> bool:
        """
        Method to check whether the teacher has already been assigned a fixed class at the given slot.
        :return - True if BUSY at the given timeslot.
        """
        # noinspection PyUnresolvedReferences
        slot_classes = self.classes.filter(time_slots=slot)
        n_commitments = slot_classes.count()
        if n_commitments == 1:
            return True
        elif n_commitments == 0:
            return False
        else:
            raise ValueError(f"Teacher {self.__str__}, {self.pk} has ended up with more than 1 FixedClass at {slot}")
