"""
Factories to be used throughout test suite when basic model instances are needed.
"""

# Standard library imports
import datetime as dt
from typing import Any

# Third party imports
import factory

# Local application imports
from data import models


class School(factory.django.DjangoModelFactory):
    """Factory for the School model. Access keys are sequenced from 1."""

    class Meta:
        model = models.School

    school_access_key = factory.Sequence(lambda n: n + 1)
    school_name = "Fake school"


class YearGroup(factory.django.DjangoModelFactory):
    """Factory for the YearGroup model. Year groups are sequenced from '1'"""

    class Meta:
        model = models.YearGroup

    school = factory.SubFactory(School)
    year_group = factory.Sequence(lambda n: str(n + 1))


class Pupil(factory.django.DjangoModelFactory):
    """Factory for the Pupil model."""

    class Meta:
        model = models.Pupil

    school = factory.SubFactory(School)
    pupil_id = factory.Sequence(lambda n: n + 1)
    firstname = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    year_group = factory.SubFactory(YearGroup)


class TimetableSlot(factory.django.DjangoModelFactory):
    """
    Factory for the TimetableSlot model.
    The slots come out as Mon 8-9, ... , Fri 8-9, Tues 8-9, ... , Fri 8-9, ...
    """

    class Meta:
        model = models.TimetableSlot

    class Params:
        slot_duration_hours = 1

    school = factory.SubFactory(School)
    slot_id = factory.Sequence(lambda n: n + 1)
    day_of_week = factory.Sequence(
        lambda n: models.WeekDay((n % len(models.WeekDay)) + 1)
    )

    @factory.sequence
    def period_starts_at(n: int) -> dt.time:
        hour = (
            (n // len(models.WeekDay)) % 8
        ) + 8  # So we have 8, 8, ..., 8, 9, ... , 9, ...
        return dt.time(hour=hour)

    @factory.lazy_attribute
    def period_ends_at(self) -> dt.time:
        hour = self.period_starts_at.hour + self.slot_duration_hours
        return dt.time(hour=hour)

    @factory.post_generation
    def relevant_year_groups(
        self,
        create: bool,
        extracted: tuple[models.YearGroup, ...] | None,
        **kwargs: Any
    ) -> None:
        """Add hte option to relate some year groups"""
        if not create:
            # Simple build (no db access) - so do nothing
            return None
        elif extracted:
            for year_group in extracted:
                self.relevant_year_groups.add(year_group)
