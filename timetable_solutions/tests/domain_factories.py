"""
Factories for domain-level objects.
"""

# Local application imports
import datetime as dt

# Third party imports
import factory

# Local application imports
from data import constants
from domain.view_timetables import timetable_component


class TimetableComponent(factory.Factory):
    """Factory of the TimetableComponent class."""

    class Meta:
        model = timetable_component.TimetableComponent

    class Params:
        duration_hours = 1

    model_instance = None
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
        hour = self.starts_at.hour + self.duration_hours
        return dt.time(hour=hour, minute=self.starts_at.minute)
