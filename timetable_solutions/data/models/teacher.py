"""Module defining the model for a teacher and any ancillary objects."""


# Django imports
from django.db import models

# Local application imports
from data.models.school import School


class TeacherQuerySet(models.QuerySet):
    """Custom queryset manager for the Teacher model"""

    def get_all_instances_for_school(self, school_id: int) -> "TeacherQuerySet":
        """Method returning the queryset of teachers registered at the given school"""
        return self.filter(school_id=school_id)

    def get_individual_teacher(self, school_id: int, teacher_id: int) -> "Teacher":
        """Method returning an individual Teacher"""
        return self.get(models.Q(school_id=school_id) & models.Q(teacher_id=teacher_id))

    def get_specific_teachers(
        self, school_id: int, teacher_ids: set[int]
    ) -> "TeacherQuerySet":
        """Method returning a queryset of teachers with the passed set of ids"""
        return self.filter(
            models.Q(school_id=school_id) & models.Q(teacher_id__in=teacher_ids)
        )

    def get_teachers_surnames_starting_with_x(
        self, school_id: int, letter: str
    ) -> "TeacherQuerySet":
        """Method returning the queryset of Teacher instances whose surname starts with the letter x."""
        query_set = self.filter(
            models.Q(school_id=school_id) & models.Q(surname__startswith=letter)
        )
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

    class Meta:
        """
        Django Meta class for the Teacher model
        """

        constraints = [
            models.UniqueConstraint(
                "school", "teacher_id", name="teacher_id_unique_for_school"
            )
        ]

    class Constant:
        """
        Additional constants to store about the Teacher model (that aren't an option in Meta)
        """

        human_string_singular = "teacher"
        human_string_plural = "teachers"

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"{self.title} {self.surname}, {self.firstname}"

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return f"{self.title} {self.surname}, {self.firstname}"

    # --------------------
    # Factories
    # --------------------

    @classmethod
    def create_new(
        cls,
        *,
        school_id: int,
        teacher_id: int,
        firstname: str,
        surname: str,
        title: str,
    ) -> "Teacher":
        """Method to create a new Teacher instance."""
        teacher = cls.objects.create(
            school_id=school_id,
            teacher_id=teacher_id,
            firstname=firstname,
            surname=surname,
            title=title,
        )
        return teacher

    @classmethod
    def delete_all_instances_for_school(cls, school_id: int) -> tuple:
        """
        Method to delete all the Teacher instances associated with a particular school.
        Note this will only work if all referencing Lessons have first been deleted.
        """
        instances = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = instances.delete()
        return outcome

    # --------------------
    # Mutators
    # --------------------
    def update(
        self,
        *,
        firstname: str | None = None,
        surname: str | None = None,
        title: str | None = None,
    ) -> "Teacher":
        """Update a teacher's details, only exposing editable fields as kwargs."""
        self.firstname = firstname or self.firstname
        self.surname = surname or self.surname
        self.title = title or self.title
        self.save(update_fields=["firstname", "surname", "title"])
        return self

    # --------------------
    # Queries
    # --------------------

    def get_lessons_per_week(self) -> int:
        """
        Method to get the number of lessons a teacher has per week.
        """
        return sum(lesson.total_required_slots for lesson in self.lessons.all())
