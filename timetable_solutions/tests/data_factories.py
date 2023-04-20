"""
Factories to be used throughout test suite when basic model instances are needed.
"""

# Standard library imports
import datetime as dt
from typing import Any

# Third party imports
import factory

# Django imports
from django.contrib.auth import models as auth_models

# Local application imports
from data import constants, models


class User(factory.django.DjangoModelFactory):
    """Factory for the default django User model."""

    class Meta:
        model = auth_models.User

    username = factory.Faker("user_name")
    password = factory.Faker("password")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.lazy_attribute(lambda obj: obj.first_name + "@test.com")


def create_user_with_known_password(
    username: str = "test_user", password: str = "password"
) -> auth_models:
    """
    Create a user with a known password for testing.

    To be able to test login, we need to know the unhashed password.
    """
    return auth_models.User.objects.create_user(username=username, password=password)


class School(factory.django.DjangoModelFactory):
    """Factory for the School model. Access keys are sequenced from 1."""

    class Meta:
        model = models.School

    school_access_key = factory.Sequence(lambda n: n + 1)
    school_name = "Fake school"


class Profile(factory.django.DjangoModelFactory):
    """Factory for the Profile model."""

    class Meta:
        model = models.Profile

    class Params:
        school_admin = factory.Trait(
            role=constants.UserRole.SCHOOL_ADMIN, approved_by_school_admin=True
        )

    user = factory.SubFactory(User)
    school = factory.SubFactory(School)
    role = constants.UserRole.TEACHER
    approved_by_school_admin = False


class YearGroup(factory.django.DjangoModelFactory):
    """Factory for the YearGroup model. Year groups are sequenced from '1'"""

    class Meta:
        model = models.YearGroup

    school = factory.SubFactory(School)
    year_group_id = factory.Sequence(lambda n: n + 1)
    year_group_name = factory.Sequence(lambda n: str(n + 1))


class Pupil(factory.django.DjangoModelFactory):
    """Factory for the Pupil model."""

    class Meta:
        model = models.Pupil

    school = factory.SubFactory(School)
    pupil_id = factory.Sequence(lambda n: n + 1)
    firstname = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    # Ensure all 'school' foreign keys are shared
    year_group = factory.SubFactory(YearGroup, school=factory.SelfAttribute("..school"))


class TimetableSlot(factory.django.DjangoModelFactory):
    """
    Factory for the TimetableSlot model.
    The slots come out as Mon 8-9, ... , Fri 8-9, Tues 9-10, ... , Fri 9-10, ...
    """

    class Meta:
        model = models.TimetableSlot

    class Params:
        slot_duration_hours = 1

    school = factory.SubFactory(School)
    slot_id = factory.Sequence(lambda n: n + 1)
    day_of_week = factory.Sequence(
        lambda n: constants.Day((n % len(constants.Day)) + 1)
    )

    @factory.sequence
    def starts_at(n: int) -> dt.time:
        hour = (
            (n // len(constants.Day)) % 8
        ) + 8  # So we have 8, 8, ..., 8, 9, ... , 9, ...
        return dt.time(hour=hour)

    @factory.lazy_attribute
    def ends_at(self) -> dt.time:
        hour = self.starts_at.hour + self.slot_duration_hours
        return dt.time(hour=hour, minute=self.starts_at.minute)

    @factory.post_generation
    def relevant_year_groups(
        self,
        create: bool,
        extracted: tuple[models.YearGroup, ...] | None,
        **kwargs: Any,
    ) -> None:
        """Add the option to relate some year groups."""
        if not create:
            # Simple build (no db access) - so do nothing
            return None
        elif extracted:
            for year_group in extracted:
                if year_group.school != self.school:
                    raise ValueError(
                        "Cannot add year group from different school to timetable slot."
                    )
                self.relevant_year_groups.add(year_group)

    @classmethod
    def get_next_consecutive_slot(
        cls, slot: models.TimetableSlot
    ) -> models.TimetableSlot:
        """Create a slot that is consecutive to the passed slot"""
        return cls(
            school=slot.school,
            day_of_week=slot.day_of_week,
            starts_at=slot.ends_at,  # Therefore consecutive
            relevant_year_groups=slot.relevant_year_groups.all(),
        )


class Teacher(factory.django.DjangoModelFactory):
    """Factory for the Teacher model."""

    class Meta:
        model = models.Teacher

    school = factory.SubFactory(School)
    teacher_id = factory.Sequence(lambda n: n + 1)
    firstname = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    title = factory.Faker("prefix")


class Classroom(factory.django.DjangoModelFactory):
    """Factory for the Classroom model."""

    class Meta:
        model = models.Classroom

    school = factory.SubFactory(School)
    classroom_id = factory.Sequence(lambda n: n + 1)
    building = "Maths building"
    room_number = factory.Sequence(lambda n: n + 1)


class Lesson(factory.django.DjangoModelFactory):
    """Factory for the Lesson model."""

    class Meta:
        model = models.Lesson

    school = factory.SubFactory(School)
    lesson_id = factory.Sequence(lambda n: f"lesson-{n}")
    subject_name = "Maths"
    teacher = factory.SubFactory(Teacher, school=factory.SelfAttribute("..school"))
    classroom = factory.SubFactory(Classroom, school=factory.SelfAttribute("..school"))
    total_required_slots = 1
    total_required_double_periods = 0

    @factory.post_generation
    def pupils(
        self, create: bool, extracted: tuple[models.Pupil, ...] | None, **kwargs: Any
    ) -> None:
        """Add the option to add some pupils."""
        if not create:
            # Simple build (no db access) - so do nothing
            return None
        elif extracted:
            for pupil in extracted:
                if pupil.school != self.school:
                    raise ValueError(
                        "Cannot add pupil from different school to lesson."
                    )
                self.pupils.add(pupil)

    @factory.post_generation
    def user_defined_time_slots(
        self,
        create: bool,
        extracted: tuple[models.TimetableSlot, ...] | None,
        **kwargs: Any,
    ) -> None:
        """Add the option to force some user defined slots."""
        if not create:
            # Simple build (no db access) - so do nothing
            return None
        elif extracted:
            for slot in extracted:
                if slot.school != self.school:
                    raise ValueError("Cannot fix slot from different school to lesson.")
                self.user_defined_time_slots.add(slot)

    @factory.post_generation
    def solver_defined_time_slots(
        self,
        create: bool,
        extracted: tuple[models.TimetableSlot, ...] | None,
        **kwargs: Any,
    ) -> None:
        """Add the option to force some solver defined slots."""
        if not create:
            # Simple build (no db access) - so do nothing
            return None
        elif extracted:
            for slot in extracted:
                if slot.school != self.school:
                    raise ValueError("Cannot add slot from different school to lesson.")
                self.solver_defined_time_slots.add(slot)

    @classmethod
    def with_n_pupils(cls, n_pupils: int = 1, **kwargs: Any) -> models.Lesson:
        """Get a lesson with n associated pupils."""
        try:
            school = kwargs.pop("school")
        except KeyError:
            school = School()
        yg = YearGroup(school=school)
        pupils = [Pupil(school=school, year_group=yg) for _ in range(0, n_pupils)]
        return cls(school=school, pupils=pupils, **kwargs)


class Break(factory.django.DjangoModelFactory):
    """Factory for the Break model."""

    class Meta:
        model = models.Break

    class Params:
        break_duration_hours = 1

    school = factory.SubFactory(School)
    break_id = factory.Sequence(lambda n: f"break-{n}")
    break_name = "Lunch"
    day_of_week = factory.Sequence(
        lambda n: constants.Day((n % len(constants.Day)) + 1)
    )
    starts_at = dt.time(hour=12)

    @factory.lazy_attribute
    def ends_at(self) -> dt.time:
        hour = self.starts_at.hour + self.break_duration_hours
        return dt.time(hour=hour, minute=self.starts_at.minute)

    @factory.post_generation
    def teachers(
        self, create: bool, extracted: tuple[models.Teacher, ...] | None, **kwargs: Any
    ) -> None:
        """Add the option to add some teachers."""
        if not create:
            # Simple build (no db access) - so do nothing
            return None
        elif extracted:
            for teacher in extracted:
                if teacher.school != self.school:
                    raise ValueError(
                        "Cannot add teacher from different school to break."
                    )
                self.teachers.add(teacher)

    @factory.post_generation
    def relevant_year_groups(
        self,
        create: bool,
        extracted: tuple[models.YearGroup, ...] | None,
        **kwargs: Any,
    ) -> None:
        """Add the option to relate some year groups."""
        if not create:
            # Simple build (no db access) - so do nothing
            return None
        elif extracted:
            for year_group in extracted:
                if year_group.school != self.school:
                    raise ValueError(
                        "Cannot add year group from different school to break."
                    )
                self.relevant_year_groups.add(year_group)
