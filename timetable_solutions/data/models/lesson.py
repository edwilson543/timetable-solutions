"""
Module defining the model for a SchoolClass, and its manager.
"""

# Django imports
from django.db import IntegrityError, models

# Local application imports
from data import constants
from data.models.classroom import Classroom
from data.models.pupil import Pupil, PupilQuerySet
from data.models.school import School
from data.models.teacher import Teacher
from data.models.timetable_slot import TimetableSlot, TimetableSlotQuerySet
from data.models.year_group import YearGroup


class NoPupilsError(Exception):
    """Raised when a lesson not having any associated pupils causes an error."""

    pass


class LessonQuerySet(models.QuerySet):
    """
    Custom queryset manager for the Lesson model
    """

    def get_all_instances_for_school(self, school_id: int) -> "LessonQuerySet":
        """Method to return the full queryset of lessons for a given school"""
        return self.filter(school_id=school_id)

    def get_individual_lesson(self, school_id: int, lesson_id: int) -> "Lesson":
        """Method to return an individual Lesson instance"""
        return self.get(models.Q(school_id=school_id) & models.Q(lesson_id=lesson_id))

    def get_lessons_requiring_solving(self, school_id: int) -> "LessonQuerySet":
        """
        Get a school's lessons where the total required slots is greater than the user defined slots count.
        """
        return self.annotate(
            n_user_slots=models.Count("user_defined_time_slots")
        ).filter(
            models.Q(school_id=school_id)
            & models.Q(total_required_slots__gt=models.F("n_user_slots"))
        )


class Lesson(models.Model):
    """
    Model representing a school lesson occurring at multiple timeslots every week
    """

    # --------------------
    # Model fields
    # --------------------

    # Basic fixed value fields
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    lesson_id = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=20)

    year_group = models.ForeignKey(
        YearGroup, related_name="lessons", on_delete=models.PROTECT, null=True
    )
    pupils = models.ManyToManyField(Pupil, related_name="lessons")

    # Teacher & classroom can be null for sport / not classroom lessons
    teacher = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name="lessons", blank=True, null=True
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="lessons",
        blank=True,
        null=True,
    )

    # Fulfillment fields
    user_defined_time_slots = models.ManyToManyField(
        TimetableSlot, related_name="user_lessons"
    )
    solver_defined_time_slots = models.ManyToManyField(
        TimetableSlot, related_name="solver_lessons"
    )

    # Fulfillment requirement fields - note that both counts include any user defined instances
    total_required_slots = models.PositiveSmallIntegerField()
    total_required_double_periods = models.PositiveSmallIntegerField()

    # Introduce a custom manager
    objects = LessonQuerySet.as_manager()

    class Meta:
        """
        Django Meta class for the Lesson model
        """

        constraints = [
            models.UniqueConstraint(
                "school", "lesson_id", name="lesson_id_unique_for_school"
            ),
            models.CheckConstraint(
                name="number_of_double_period_slots_cannot_exceed_total_required_slots",
                check=models.Q(
                    total_required_slots__gte=models.F("total_required_double_periods")
                    * 2
                ),
            ),
        ]

    class Constant:
        """
        Additional constants to store about the Lesson model (that aren't an option in Meta)
        """

        human_string_singular = "lesson"
        human_string_plural = "lessons"

        # Field names
        pupils = "pupils"
        user_defined_time_slots = "user_defined_time_slots"
        solver_defined_time_slots = "solver_defined_time_slots"

    def __str__(self) -> str:
        """String representation of the model for the django admin site"""
        return f"{self.lesson_id}".title().replace("_", " ")

    def __repr__(self) -> str:
        """String representation of the model for debugging"""
        return f"{self.school}: {self.lesson_id}"

    # --------------------
    # Factories
    # --------------------

    @classmethod
    def create_new(
        cls,
        school_id: int,
        lesson_id: str,
        subject_name: str,
        total_required_slots: int,
        total_required_double_periods: int,
        teacher: Teacher | None = None,
        classroom: Classroom | None = None,
        year_group: YearGroup | None = None,
        pupils: PupilQuerySet | None = None,
        user_defined_time_slots: TimetableSlotQuerySet | None = None,
    ) -> "Lesson":
        """
        Create a new Lesson instance.
        """
        lesson = cls.objects.create(
            school_id=school_id,
            lesson_id=lesson_id,
            subject_name=subject_name,
            total_required_slots=total_required_slots,
            total_required_double_periods=total_required_double_periods,
            teacher=teacher,
            classroom=classroom,
            year_group=year_group,
        )

        if pupils:
            lesson.add_pupils(pupils=pupils)
        if user_defined_time_slots:
            lesson.add_user_defined_time_slots(time_slots=user_defined_time_slots)

        return lesson

    @classmethod
    def delete_all_lessons_for_school(cls, school_id: int) -> tuple:
        """Method deleting all entries for a school in the Lesson table"""
        lessons = cls.objects.get_all_instances_for_school(school_id=school_id)
        outcome = lessons.delete()
        return outcome

    @classmethod
    def delete_solver_solution_for_school(cls, school_id: int) -> None:
        """Method deleting all associations in the solver_defined_time_slots field, of a school's Lessons"""
        lessons = cls.objects.get_all_instances_for_school(school_id=school_id)
        for lesson in lessons:
            lesson.solver_defined_time_slots.clear()

    # --------------------
    # Mutators
    # --------------------

    def update(
        self,
        *,
        subject_name: str | None = None,
        teacher: Teacher | None = None,
        classroom: Classroom | None = None,
        total_required_slots: int | None = None,
        total_required_double_periods: int | None = None,
    ) -> "Lesson":
        """
        Update a lesson in the db.

        Excludes M2M fields and any other fields that it does not make
        sense to update post-creation.
        """
        self.subject_name = subject_name or self.subject_name
        self.teacher = teacher or self.teacher
        self.classroom = classroom or self.classroom
        self.total_required_slots = total_required_slots or self.total_required_slots
        self.total_required_double_periods = (
            total_required_double_periods or self.total_required_double_periods
        )
        self.save(
            update_fields=[
                "subject_name",
                "teacher",
                "classroom",
                "total_required_slots",
                "total_required_double_periods",
            ]
        )
        return self

    def add_pupil(self, pupil: Pupil) -> None:
        """
        Add a pupil to this Lesson.
        """
        self.pupils.add(pupil)

    def remove_pupil(self, pupil: Pupil) -> None:
        """
        Remove a pupil from this Lesson.
        """
        self.pupils.remove(pupil)

    def add_user_defined_time_slot(self, slot: TimetableSlot) -> None:
        """
        Add a user-defined time slots to this lesson.
        """
        self.user_defined_time_slots.add(slot)

    def remove_user_defined_time_slot(self, slot: TimetableSlot) -> None:
        """
        Add a user-defined time slots to this lesson.
        """
        self.user_defined_time_slots.remove(slot)

    def add_pupils(self, pupils: PupilQuerySet | Pupil) -> None:
        """
        Add some pupils to this Lesson.
        """
        self.pupils.add(*pupils)

    def add_user_defined_time_slots(self, time_slots: TimetableSlotQuerySet) -> None:
        """
        Add some user-defined time slots to this lesson.
        """
        existing_user_slots = self.user_defined_time_slots.all()

        if (time_slots | existing_user_slots).distinct().count() > self.total_required_slots:
            raise IntegrityError(
                f"User tried to define more slots for {repr(self)} than the total requirement"
            )
        self.user_defined_time_slots.add(*time_slots)

    def add_solver_defined_time_slots(self, time_slots: TimetableSlotQuerySet) -> None:
        """
        Add the solver-generated solution slots for this lesson.
        """
        if intersection := time_slots & self.user_defined_time_slots.all():
            raise IntegrityError(
                f"Tried to set slots: {intersection} that appear in user defined slots "
                f"as solver defined for lesson {repr(self)}!"
            )
        self.solver_defined_time_slots.add(*time_slots)

    # --------------------
    # Queries - view timetables logic
    # --------------------

    def get_all_time_slots(self) -> TimetableSlotQuerySet:
        """
        Method to provide ALL time slots when a particular lesson is known to take place.
        The .distinct() prevents duplicates, but there should be none anyway - for some reason, there seems to be a bug
        where duplicates are created within one of the individual query sets, at the point of combining.
        """
        return (
            (self.user_defined_time_slots.all() | self.solver_defined_time_slots.all())
            .distinct()
            .order_by("day_of_week", "starts_at")
        )

    # --------------------
    # Queries - solver logic
    # --------------------

    def get_n_solver_slots_required(self) -> int:
        """
        Method to calculate the total additional number of slots that the solver must produce.
        """
        return self.total_required_slots - self.user_defined_time_slots.all().count()

    def get_n_solver_double_periods_required(self) -> int:
        """
        Method to calculate the total additional number of double periods that the solver must produce.
        """
        total_user_defined = sum(
            self.get_user_defined_double_period_count_on_day(day_of_week=day)
            for day in constants.Day.values  # Note will just be 0, so no need to restrict
        )
        return self.total_required_double_periods - total_user_defined

    def get_user_defined_double_period_count_on_day(
        self, day_of_week: constants.Day
    ) -> int:
        """
        Method to count the number of user-defined double periods on the given day
        To achieve this, we iterate through the full set of ordered TimeTable Slot
        :return - an integer specifying how many double periods the Lesson instance has on the given day
        """

        year_group = self.get_associated_year_group()
        # Note that slots will be ordered in time, using the TimetableSlot Meta class
        user_slots_on_day = (
            self.user_defined_time_slots.all().get_timeslots_on_given_day(
                school_id=self.school.school_access_key,
                day_of_week=day_of_week,
                year_group=year_group,
            )
        )

        # Set initial parameters affected by the for loop
        double_period_count = 0
        previous_slot = None

        for slot in user_slots_on_day:
            if (previous_slot is not None) and slot.check_if_slots_are_consecutive(
                other_slot=previous_slot
            ):
                double_period_count += 1
            previous_slot = slot

        return double_period_count

    def get_usable_days_of_week(self) -> list[constants.Day]:
        """
        Get the weekdays that a lesson may be taught on, based on its associated timeslots.
        :return - days_list - a list of the days, sorted from lowest to highest.
        """
        associated_slots = self.get_associated_timeslots()
        days = {
            slot.day_of_week for slot in associated_slots
        }  # We only want unique days
        days_list = sorted(list(days))
        return days_list

    def get_associated_timeslots(self) -> TimetableSlotQuerySet:
        """
        Get the timetable slots associated with a particular Lesson (via its year group).
        We intentionally don't check e.g. whether the lesson already occurs at one of these slots,
        as this is solver domain logic.
        """
        year_group = self.get_associated_year_group()
        return year_group.slots.all()

    def get_associated_year_group(self) -> YearGroup:
        """
        Get the year group a Lesson will be taught to.
        """
        if self.year_group:
            return self.year_group
        all_pupils = self.pupils.all()
        if all_pupils.count() > 0:
            return all_pupils.first().year_group
        else:
            raise NoPupilsError(
                f"Lesson: {repr(self)} does not have any pupils, therefore cannot retrieve associated year group"
            )
