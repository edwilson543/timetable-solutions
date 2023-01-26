# Standard library imports
from collections import OrderedDict
import datetime as dt

# Local application imports
from data import constants as data_constants
from data import models
from domain.view_timetables import timetable_component
from domain.view_timetables import constants as view_timetable_constants


class Timetable:
    """Class to store and construct timetables."""

    def __init__(
        self, lessons: models.LessonQuerySet, breaks: models.BreakQuerySet | None
    ) -> None:
        self._lessons = lessons
        self._breaks = breaks

        # Iterable data structure for a timetable, to be filled
        self.timetable: OrderedDict = OrderedDict(
            [
                (data_constants.Day.MONDAY, []),
                (data_constants.Day.TUESDAY, []),
                (data_constants.Day.WEDNESDAY, []),
                (data_constants.Day.THURSDAY, []),
                (data_constants.Day.FRIDAY, []),
                (data_constants.Day.SATURDAY, []),
                (data_constants.Day.SUNDAY, []),
            ]
        )

    def make_timetable(
        self,
    ) -> OrderedDict[data_constants.Day, list[timetable_component.TimetableComponent]]:
        """Make a colourful timetable where the slots can start at different times across days."""
        self._make_components_from_lessons()
        self._make_components_from_breaks()

        min_timetable_start = min(
            component.starts_at for component in self._all_components
        )
        max_timetable_finish = max(
            component.ends_at for component in self._all_components
        )

        for day, components in self.timetable.items():
            if not components:
                continue
            components = _sort_components(components)
            components = _merge_consecutive_components(components)
            components = _fill_gaps_with_free_periods(
                components,
                timetable_starts_at=min_timetable_start,
                timetable_ends_at=max_timetable_finish,
            )
            components = _set_percentage_of_days_timetable(components)

            self.timetable[day] = components

        return self.timetable

    # --------------------
    # Mutators
    # --------------------

    def _make_components_from_lessons(self) -> None:
        """
        Make all the timetable components from the LessonQuerySet.
        """
        colour_mapping = _get_lesson_colours(self._lessons)
        for lesson in self._lessons:
            # Colour code will just be None if mapping wasn't set
            colour_code = colour_mapping.get(lesson.lesson_id)
            for slot in lesson.get_all_time_slots():
                component = timetable_component.TimetableComponent.from_lesson_slot(
                    lesson=lesson, slot=slot, colour_code=colour_code
                )
                self._add_component_to_day(component, day=slot.day_of_week)

    def _make_components_from_breaks(self) -> None:
        """Make all the timetable components from the BreakQuerySet."""
        if self._breaks:
            for break_ in self._breaks:
                component = timetable_component.TimetableComponent.from_break(
                    break_=break_,
                )
                self._add_component_to_day(component, day=break_.day_of_week)

    def _add_component_to_day(
        self, component: timetable_component.TimetableComponent, day: data_constants.Day
    ) -> None:
        """Add the component to the relevant day of the timetable."""
        self.timetable[day].append(component)

    # --------------------
    # Properties
    # --------------------

    @property
    def _all_components(self) -> list[timetable_component.TimetableComponent]:
        """Combine the components on all days into a single list."""
        return [
            component
            for components in self.timetable.values()
            for component in components
        ]


def _sort_components(
    components: list[timetable_component.TimetableComponent],
) -> list[timetable_component.TimetableComponent]:
    """
    Sort the components by their start time.
    Upstream validation should mean this is the same as sorting by the end time.
    """
    return sorted(components, key=lambda component: component.starts_at)


def _merge_consecutive_components(
    components: list[timetable_component.TimetableComponent],
) -> list[timetable_component.TimetableComponent]:
    """
    Combine any consecutive components into one component.
    This covers doubles, triples or more of the same component.
    """
    previous_component = None
    new_components = []

    for component in components:

        if previous_component is None:
            new_components.append(component)
            previous_component = component
            continue

        try:
            new_component = timetable_component.TimetableComponent.merge(
                first=previous_component, other=component
            )
            # Replacing the last component ensures we never duplicate a component
            new_components[-1] = new_component
            previous_component = new_component
        except timetable_component.CannotMergeError:
            new_components.append(component)
            previous_component = component

    return new_components


def _fill_gaps_with_free_periods(
    components: list[timetable_component.TimetableComponent],
    timetable_starts_at: dt.time,
    timetable_ends_at: dt.time,
) -> list[timetable_component.TimetableComponent]:
    """
    Fill any gaps (durations of time) with a new free period component.

    :param components: The gappy timetable components for a single day
    :param timetable_starts_at / timetable_ends_at: The span of time that should be considered
    free periods if there is no existing component at.
    """
    last_period_ended_at = timetable_starts_at
    new_components = []

    # Iteratively use free periods as stop gaps
    for component in components:
        if component.starts_at != last_period_ended_at:
            # There was a gap between this and previous component, so make a free period
            free_period = timetable_component.TimetableComponent.free_period(
                starts_at=last_period_ended_at,
                ends_at=component.starts_at,
                day_of_week=component.day_of_week,
            )
            new_components.append(free_period)

        new_components.append(component)
        last_period_ended_at = component.ends_at

    # Iteration cannot add a free period to end of day, so do this now
    last_component = new_components[-1]
    if last_component.ends_at != timetable_ends_at:
        free_period = timetable_component.TimetableComponent.free_period(
            starts_at=last_component.ends_at,
            ends_at=timetable_ends_at,
            day_of_week=last_component.day_of_week,
        )
        new_components.append(free_period)

    return new_components


def _set_percentage_of_days_timetable(
    components: list[timetable_component.TimetableComponent],
) -> list[timetable_component.TimetableComponent]:
    """Divide each component's duration by the length of the day"""
    total_duration = sum(component.duration_hours for component in components)
    for component in components:
        percentage = component.duration_hours / total_duration
        component.set_percentage_of_days_timetable(percentage)
    return components


def _get_lesson_colours(lessons: models.LessonQuerySet) -> dict[str, str]:
    """Get a colour"""
    ordered_lessons = lessons.order_by("total_required_slots").reverse()
    return {
        lesson.lesson_id: view_timetable_constants.Colour.get_colour(rank)
        for rank, lesson in enumerate(ordered_lessons)
    }
