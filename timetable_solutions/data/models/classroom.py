"""Module defining the model for a school_id classroom and any ancillary objects."""


# Django imports
from django.db import models

# Local application imports
from data.models.school import School


class ClassroomQuerySet(models.QuerySet):
    """Custom queryset manager for the Classroom model"""

    def get_all_instances_for_school(self, school_id: int) -> "ClassroomQuerySet":
        """Method to return the full queryset of classrooms for a given school"""
        return self.filter(school_id=school_id)

    def get_individual_classroom(
        self, school_id: int, classroom_id: int
    ) -> "ClassroomQuerySet":
        """Method to return an individual classroom instance"""
        return self.get(
            models.Q(school_id=school_id) & models.Q(classroom_id=classroom_id)
        )


class Classroom(models.Model):
    """
    Model storing the classroom (location) in which a Lesson takes place.
    Currently, a lesson must take place in exactly one classroom - a future extension could be to also optimise
    based on minimising the number of distinct classrooms required.
    """

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    classroom_id = models.IntegerField()
    building = models.CharField(max_length=20)
    room_number = models.IntegerField()

    # Introduce a custom manager
    objects = ClassroomQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the Classroom model
        """

        constraints = [
            models.UniqueConstraint(
                "school",
                "classroom_id",
                name="classroom_id_unique_for_school",
            ),
            models.UniqueConstraint(
                "school",
                "building",
                "room_number",
                name="classroom_building_room_number_unique_for_school",
            ),
        ]

    class Constant:
        """
        Additional constants to store about the Classroom model (that aren't an option in Meta)
        """

        human_string_singular = "classroom"
        human_string_plural = "classrooms"

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"{self.building},  {self.room_number}"

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return f"{self.building},  {self.room_number}"

    # --------------------
    # Factories
    # --------------------

    @classmethod
    def create_new(
        cls, school_id: int, classroom_id: int, building: str, room_number: int
    ) -> "Classroom":
        """
        Method to create a new Classroom instance.
        """
        classroom = cls.objects.create(
            school_id=school_id,
            classroom_id=classroom_id,
            building=building,
            room_number=room_number,
        )
        return classroom

    @classmethod
    def delete_all_instances_for_school(cls, school_id: int) -> tuple:
        """
        Method to delete all the Classroom instances associated with a particular school
        """
        instances = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = instances.delete()
        return outcome

    # --------------------
    # Mutators
    # --------------------

    def update(
        self, building: str | None = None, room_number: int | None = None
    ) -> "Classroom":
        """
        Update the editable fields of a classroom in the db.
        """
        self.building = building or self.building
        self.room_number = room_number or self.room_number
        self.save(update_fields=["building", "room_number"])
        return self

    # --------------------
    # Queries
    # --------------------

    def get_lessons_per_week(self) -> int:
        """
        Method to get the number of lessons taught per week in a classroom.
        """
        return sum(lesson.total_required_slots for lesson in self.lessons.all())
