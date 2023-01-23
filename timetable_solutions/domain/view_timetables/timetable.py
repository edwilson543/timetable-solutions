from collections import OrderedDict
import datetime as dt

from data import constants
from data import models
from timetable_component import TimetableComponent


def get_timetable(
    entity: models.Pupil | models.Teacher | models.Classroom,
) -> "Timetable":
    # TODO -> to become an entrypoint / use case
    # Get their lessons
    # Get their breaks
    # Instantiate a Timetable
    pass


class TimetableIncompleteError(Exception):
    """Raised if a timetable attribute is accessed prematurely."""

    pass


class Timetable:
    def __init__(
        self, lessons: models.LessonQuerySet, breaks: models.BreakQuerySet | None
    ) -> None:
        self._lessons = lessons
        self._breaks = breaks

        # Iterable data structure for a timetable, to be filled
        self.timetable: OrderedDict[
            constants.Day, list[TimetableComponent]
        ] = OrderedDict(
            [
                (constants.Day.MONDAY, []),
                (constants.Day.TUESDAY, []),
                (constants.Day.WEDNESDAY, []),
                (constants.Day.THURSDAY, []),
                (constants.Day.FRIDAY, []),
                (constants.Day.SATURDAY, []),
                (constants.Day.SUNDAY, []),
            ]
        )

    # --------------------
    # Timetable styles
    # --------------------
    def staggered_and_coloured(self):
        """Make a colourful timetable where the slots can start at different times across days."""
        self._make_components_from_lessons(colour=True)
        if self._breaks:
            self._make_components_from_breaks(colour=True)
        min_timetable_start = min(
            component.starts_at for component in self._all_components
        )
        max_timetable_finish = max(
            component.ends_at for component in self._all_components
        )

        for day, components in self.timetable.items():
            if not components:
                continue
            # TODO - check order of below methods
            # TODO - maybe fill blank e.g. tuesdays if monday and wednesday in use
            # TODO - any more functional?
            components = self._sort_components(components)
            components = self._merge_consecutive_components(components)
            components = self._fill_gaps_with_free_periods(components)
            components = self._set_percentage_of_days_timetable(components)

            self.timetable[day] = components

    # --------------------
    # Mutators
    # --------------------

    def _make_components_from_lessons(self, colour: bool) -> None:
        # if colour get lesson colours
        # for lesson in lessons
        #   get colour else none
        #   c = TimetableComponent.from_lesson(lesson, col)
        #   self._add_component_to_day(c, lesson)
        pass

    def _make_components_from_breaks(self, colour: bool) -> None:
        pass

    def _add_component_to_day(
        self, component: TimetableComponent, day: constants.Day
    ) -> None:
        pass

    def _set_min_timetable_start(self) -> None:
        all_components = self._all_components
        if len(all_components) == 0:
            raise TimetableIncompleteError(
                "No timetable components are present for this timetable."
            )
        else:
            self._min_timetable_start = min(
                component.starts_at for component in all_components
            )

    def _set_max_timetable_finish(self) -> float:
        pass

    @staticmethod
    def _sort_components(
        components: list[TimetableComponent],
    ) -> list[TimetableComponent]:
        pass

    @staticmethod
    def _merge_consecutive_components(
        components: list[TimetableComponent],
    ) -> list[TimetableComponent]:
        pass

    def _fill_gaps_with_free_periods(
        self, components: list[TimetableComponent]
    ) -> list[TimetableComponent]:
        pass

    @staticmethod
    def _set_percentage_of_days_timetable(
        components: list[TimetableComponent],
    ) -> list[TimetableComponent]:
        pass

    # --------------------
    # Properties
    # --------------------

    @property
    def _all_components(self) -> list[TimetableComponent]:
        return sum(components for components in self.timetable.values())
