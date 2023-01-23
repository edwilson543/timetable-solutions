# Standard library imports
import dataclasses
import datetime as dt

# Local application imports
from data import constants
from data import models


@dataclasses.dataclass(frozen=True)
class TimetableComponent:
    """Generalised component of a timetable that will be shown in the UI."""

    model_instance: models.Lesson | models.Break | None
    starts_at: dt.time
    ends_at: dt.time
    day_of_week: constants.Day

    # These get set down stream
    hexadecimal_color_code: str | None = None
    percentage_of_days_timetable: float | None = None

    # --------------------
    # Factories
    # --------------------
    @classmethod
    def from_lesson(
        cls, lesson: models.Lesson, colour_code: str
    ) -> "TimetableComponent":
        pass

    @classmethod
    def from_break(cls, break_: models.Break) -> "TimetableComponent":
        pass

    @classmethod
    def free_period(cls, starts_at: dt.time, ends_at: dt.time) -> "TimetableComponent":
        pass

    # --------------------
    # Mutators
    # --------------------
    def set_percentage_of_days_timetable(self) -> None:
        pass

    # --------------------
    # Properties
    # --------------------

    @property
    def display_name(self) -> str:
        """Text to be shown at the top o"""
        if self.is_lesson:
            return self.model_instance.subject_name.title()
        elif self.is_break:
            return self.model_instance.break_name.title()
        else:
            return "Free"

    @property
    def is_lesson(self) -> bool:
        return isinstance(self.model_instance, models.Lesson)

    @property
    def is_break(self) -> bool:
        return isinstance(self.model_instance, models.Break)

    @property
    def is_free_period(self) -> bool:
        return not self.model_instance

    @property
    def duration_hours(self) -> float:
        """Number of hours (as a decimal) a component lasts."""
        dur_delta = dt.timedelta(
            hours=self.ends_at.hour, minutes=self.ends_at.minute
        ) - dt.timedelta(hours=self.starts_at.hour, minutes=self.starts_at.minute)
        seconds_per_hour = 3600
        return dur_delta.seconds / seconds_per_hour
