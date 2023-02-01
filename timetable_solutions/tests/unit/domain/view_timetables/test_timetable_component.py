# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants as data_constants
from domain.view_timetables import constants as view_timetables_constants
from domain.view_timetables.timetable_component import (
    TimetableComponent,
    CannotMergeError,
)
from tests import data_factories
from tests import domain_factories


class TestTimetableComponent:
    """Unit tests on the TimetableComponent class"""

    # --------------------
    # Factories tests
    # --------------------
    def test_from_lesson_slot_is_valid_constructor(self):
        """Ensure we can make a component direct from a lesson/slot."""
        # Make some fake db content for the component
        school = data_factories.School.build()
        slot = data_factories.TimetableSlot.build(school=school)
        lesson = data_factories.Lesson.build(
            solver_defined_time_slots=(slot,), school=school
        )

        component = TimetableComponent.from_lesson_slot(
            lesson=lesson, slot=slot, colour_code=""
        )

        # Check attributes correctly set
        assert component.model_instance == lesson
        assert component.starts_at == slot.starts_at
        assert component.ends_at == slot.ends_at
        assert component.day_of_week == slot.day_of_week

        # Check properties are as expected
        assert component.display_name.upper() == lesson.subject_name.upper()
        assert component.is_lesson

    def test_from_break_is_valid_constructor(self):
        """Ensure we can make a component direct from a break."""
        # Make some fake db content for the component
        break_ = data_factories.Break.build()

        component = TimetableComponent.from_break(break_=break_)

        # Check attributes correctly set
        assert component.model_instance == break_
        assert component.starts_at == break_.starts_at
        assert component.ends_at == break_.ends_at
        assert component.day_of_week == break_.day_of_week

        # Check properties are as expected
        assert component.display_name.upper() == break_.break_name.upper()
        assert component.is_break

    def test_free_period_is_valid_constructor(self):
        """Ensure we can make a component direct from a lesson/slot."""
        component = TimetableComponent.free_period(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
        )

        # Check attributes correctly set
        assert component.model_instance is None
        assert component.starts_at == dt.time(hour=8)
        assert component.ends_at == dt.time(hour=9)
        assert component.day_of_week == data_constants.Day.MONDAY

        # Check properties are as expected
        assert component.display_name == view_timetables_constants.FREE
        assert component.is_free_period

    def test_merge_is_valid_constructor(self):
        """Ensure we can make a new component from the merge constructor."""
        # Get a lesson for them to share
        lesson = data_factories.Lesson.build()

        component = domain_factories.TimetableComponent(
            model_instance=lesson,
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
        )
        other = domain_factories.TimetableComponent(
            model_instance=lesson,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=data_constants.Day.MONDAY,
        )

        new_component = TimetableComponent.merge(component, other)

        # Check attributes correctly set
        assert new_component.model_instance == lesson
        assert new_component.starts_at == dt.time(hour=8)
        assert new_component.ends_at == dt.time(hour=10)
        assert new_component.day_of_week == data_constants.Day.MONDAY

    def test_merge_fails_for_components_from_different_lessons(self):
        # Get a lesson for them to share
        lesson = data_factories.Lesson.build()
        other_lesson = data_factories.Lesson.build()

        # Put the slots at the same time
        component = domain_factories.TimetableComponent(
            model_instance=lesson,
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
        )
        other = domain_factories.TimetableComponent(
            model_instance=other_lesson,
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
        )

        with pytest.raises(CannotMergeError):
            TimetableComponent.merge(component, other)

    def test_merge_fails_for_components_that_arent_consecutive(self):
        # Get a lesson for them to share
        lesson = data_factories.Lesson.build()

        # Put the slots at non-consecutive times
        component = domain_factories.TimetableComponent(
            model_instance=lesson,
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
        )
        other = domain_factories.TimetableComponent(
            model_instance=lesson,
            starts_at=dt.time(hour=9, minute=15),
            ends_at=dt.time(hour=10),
            day_of_week=data_constants.Day.MONDAY,
        )

        with pytest.raises(CannotMergeError):
            TimetableComponent.merge(component, other)

    def test_merge_fails_for_components_that_are_on_different_days(self):
        # Get a lesson for them to share
        lesson = data_factories.Lesson.build()

        # Put the slots at consecutive times but on different days
        component = domain_factories.TimetableComponent(
            model_instance=lesson,
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
        )
        other = domain_factories.TimetableComponent(
            model_instance=lesson,
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=data_constants.Day.TUESDAY,
        )

        with pytest.raises(CannotMergeError):
            TimetableComponent.merge(component, other)

    # --------------------
    # Properties tests
    # --------------------

    @pytest.mark.parametrize(
        "starts_at,ends_at,expected_duration",
        [
            (dt.time(hour=8), dt.time(hour=9), 1),
            (dt.time(hour=9, minute=30), dt.time(hour=10, minute=15), 0.75),
        ],
    )
    def test_duration_hours(self, starts_at, ends_at, expected_duration):
        """Test the correct duration is computed."""
        component = domain_factories.TimetableComponent(
            starts_at=starts_at, ends_at=ends_at
        )

        assert component.duration_hours == expected_duration
