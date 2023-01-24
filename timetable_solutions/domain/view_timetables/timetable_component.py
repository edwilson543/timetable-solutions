# Standard library imports
import dataclasses
import datetime as dt

# Local application imports
from data import constants as data_constants
from data import models
from domain.view_timetables import constants as view_timetables_constants


class CannotMergeError(Exception):
    """Raised when two timetable components are incompatible for merging."""

    pass


@dataclasses.dataclass
class TimetableComponent:
    """Generalised component of a timetable that will be shown in the UI."""

    model_instance: models.Lesson | models.Break | None
    starts_at: dt.time
    ends_at: dt.time
    day_of_week: data_constants.Day

    # Fields to feed into the css.
    hexadecimal_color_code: str | None = None
    percentage_of_days_timetable: float | None = None

    # --------------------
    # Factories
    # --------------------
    @classmethod
    def from_lesson_slot(
        cls, lesson: models.Lesson, slot: models.TimetableSlot, colour_code: str
    ) -> "TimetableComponent":
        """Make a component from a slot at which a lesson occurs."""
        return cls(
            model_instance=lesson,
            starts_at=slot.period_starts_at,
            ends_at=slot.period_ends_at,
            day_of_week=slot.day_of_week,
            hexadecimal_color_code=colour_code,
        )

    @classmethod
    def from_break(cls, break_: models.Break, colour_code: str) -> "TimetableComponent":
        """Make a component from a Break instance."""
        return cls(
            model_instance=break_,
            starts_at=break_.break_starts_at,
            ends_at=break_.break_ends_at,
            day_of_week=break_.day_of_week,
            hexadecimal_color_code=colour_code,
        )

    @classmethod
    def free_period(
        cls,
        starts_at: dt.time,
        ends_at: dt.time,
        day_of_week: data_constants.Day,
        colour_code: str,
    ) -> "TimetableComponent":
        """Make a component to fill a free period with."""
        return cls(
            model_instance=None,
            starts_at=starts_at,
            ends_at=ends_at,
            day_of_week=day_of_week,
            hexadecimal_color_code=colour_code,
        )

    @classmethod
    def merge(
        cls, first: "TimetableComponent", other: "TimetableComponent"
    ) -> "TimetableComponent":
        """Merge two consecutive components into one new component spanning their duration."""
        if first.model_instance != other.model_instance:
            raise CannotMergeError(
                "Cannot merge two timetable components that do not share the same model instance."
            )

        middles = {
            max(first.starts_at, other.starts_at),
            min(first.ends_at, other.ends_at),
        }
        if len(middles) > 1:
            raise CannotMergeError(
                "Timetable components must be consecutive to be merged."
            )

        if first.day_of_week != other.day_of_week:
            raise CannotMergeError(
                "Cannot merge two timetable components on different days."
            )

        starts_at = min(first.starts_at, other.starts_at)
        ends_at = max(first.ends_at, other.ends_at)
        return TimetableComponent(
            model_instance=first.model_instance,
            starts_at=starts_at,
            ends_at=ends_at,
            day_of_week=first.day_of_week,
            hexadecimal_color_code=first.hexadecimal_color_code,
        )

    # --------------------
    # Mutators
    # --------------------
    def set_percentage_of_days_timetable(self, value: float) -> None:
        self.percentage_of_days_timetable = value

    # --------------------
    # Properties
    # --------------------

    @property
    def display_name(self) -> str:
        """Text to be shown at the top of a rendered TimetableComponent."""
        # mypy doesn't follow the property definitions properly, hence ignores
        if self.is_lesson:
            return self.model_instance.subject_name.title()  # type: ignore
        elif self.is_break:
            return self.model_instance.break_name.title()  # type: ignore
        else:
            return view_timetables_constants.FREE

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
