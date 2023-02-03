"""Tests the timetables are constructed as expected."""

# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Local application imports
from data import constants as data_constants
from data import models
from domain.view_timetables import constants as view_timetable_constants
from domain.view_timetables import timetable
from tests import data_factories


def get_lesson_with_slot(
    starts_at: dt.time,
    ends_at: dt.time,
    day_of_week: data_constants.Day,
    school: models.School,
) -> models.Lesson:
    """
    Helper factory that is specific to the requirements of this module.
    It creates a lesson with a single user defined slot.
    """
    slot = data_factories.TimetableSlot(
        starts_at=starts_at,
        ends_at=ends_at,
        day_of_week=day_of_week,
        school=school,
    )
    return data_factories.Lesson(user_defined_time_slots=(slot,), school=school)


@pytest.mark.django_db
class TestTimetableMakeTimetableMergeConsecutive:
    """Tests for the component merging functionality of make_timetable."""

    @pytest.mark.parametrize("n_consecutive_lessons", [0, 1, 2, 3])
    def test_make_timetable_from_consecutive_lessons(self, n_consecutive_lessons):
        """Expect the lesson(s) to be merged into a single component."""
        school = data_factories.School()

        # Make the first of the consecutive slots
        slot_0 = data_factories.TimetableSlot(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )
        slots = [slot_0]

        # Create back to back slots as specified in parameters
        for _ in range(0, n_consecutive_lessons):
            slots.append(
                data_factories.TimetableSlot.get_next_consecutive_slot(slots[-1])
            )
        lesson = data_factories.Lesson(user_defined_time_slots=slots, school=school)

        # Make lesson into a queryset and use to get a timetable
        lessons = models.Lesson.objects.filter(pk=lesson.pk)
        tt_object = timetable.Timetable(lessons=lessons, breaks=None)
        tt_dict = tt_object.make_timetable()

        # Check just the one, merged lesson on Monday
        mon = tt_dict[data_constants.Day.MONDAY]
        assert len(mon) == 1
        merged_lesson = mon[0]
        assert merged_lesson.starts_at == dt.time(hour=8)

        expected_end_hour = 8 + 1 + n_consecutive_lessons
        assert merged_lesson.ends_at == dt.time(hour=expected_end_hour)
        assert merged_lesson.model_instance == lesson
        # This is the only lesson so we expect it to occupy 100% of the day
        assert mon[0].percentage_of_days_timetable == 100

    def test_make_timetable_from_back_to_back_but_different_lessons(self):
        """Expect the lesson(s) to remain distinct."""
        school = data_factories.School()

        # Make the distinct lessons, with the second starting when the other finishes
        lesson_0 = get_lesson_with_slot(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=8, minute=45),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )
        lesson_1 = get_lesson_with_slot(
            starts_at=dt.time(hour=8, minute=45),
            ends_at=dt.time(hour=10),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )

        # Make lesson into a queryset and use to get a timetable
        lessons = models.Lesson.objects.filter(pk__in=[lesson_0.pk, lesson_1.pk])
        tt_object = timetable.Timetable(lessons=lessons, breaks=None)
        tt_dict = tt_object.make_timetable()

        # Check we still have two distinct lessons on Monday
        mon = tt_dict[data_constants.Day.MONDAY]
        assert len(mon) == 2
        assert mon[0].model_instance == lesson_0
        assert mon[1].model_instance == lesson_1

        # Check the percentages - the split is 45m versus 1h 15m
        assert mon[0].percentage_of_days_timetable == 37.5
        assert mon[1].percentage_of_days_timetable == 62.5


@pytest.mark.django_db
class TestTimetableMakeTimetableFreePeriods:
    """Tests for the free period filling functionality of make_timetable."""

    def test_make_timetable_from_two_lessons_on_different_days_at_same_time(self):
        """Expect no free periods, just 2 lesson components."""
        school = data_factories.School()

        # Get our two lessons at the same time, but on different days
        mon_lesson = get_lesson_with_slot(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )
        tue_lesson = get_lesson_with_slot(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.TUESDAY,
            school=school,
        )

        # Make them into a queryset and use to get a timetable
        lessons = models.Lesson.objects.filter(pk__in=[mon_lesson.pk, tue_lesson.pk])
        tt_object = timetable.Timetable(lessons=lessons, breaks=None)
        tt_dict = tt_object.make_timetable()

        # Check each day has one component, of the same length
        mon = tt_dict[data_constants.Day.MONDAY]
        tue = tt_dict[data_constants.Day.TUESDAY]

        assert len(mon) == len(tue) == 1
        assert mon[0].model_instance == mon_lesson
        assert tue[0].model_instance == tue_lesson

    def test_make_timetable_from_two_lessons_same_day_with_gap(self):
        """Expect the gap to be filled with a free period."""
        school = data_factories.School()

        # Get our two lessons with a gap between them
        lesson_0 = get_lesson_with_slot(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )
        lesson_1 = get_lesson_with_slot(
            starts_at=dt.time(hour=10),
            ends_at=dt.time(hour=11),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )

        # Make them into a queryset and use to get a timetable
        lessons = models.Lesson.objects.filter(pk__in=[lesson_0.pk, lesson_1.pk])
        tt_object = timetable.Timetable(lessons=lessons, breaks=None)
        tt_dict = tt_object.make_timetable()

        # Check we have two lessons and a free period
        mon = tt_dict[data_constants.Day.MONDAY]
        assert len(mon) == 3

        lesson_component_0 = mon[0]
        assert lesson_component_0.starts_at == dt.time(hour=8)

        free_period = mon[1]
        assert free_period.starts_at == dt.time(hour=9)
        assert free_period.ends_at == dt.time(hour=10)

        lesson_component_1 = mon[2]
        assert lesson_component_1.starts_at == dt.time(hour=10)

        # Check the percentages - the split is 45m versus 1h 15m
        percentages = list({comp.percentage_of_days_timetable for comp in mon})
        assert len(percentages) == 1
        assert list(percentages)[0] == pytest.approx(100 / 3)

    def test_make_timetable_from_two_lessons_on_different_days_at_different_times(self):
        """Expect free periods to be used to make the days the same length."""
        school = data_factories.School()

        # Get our two lessons at different times and on different days
        mon_lesson = get_lesson_with_slot(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )
        tue_lesson = get_lesson_with_slot(
            starts_at=dt.time(hour=9),
            ends_at=dt.time(hour=10),
            day_of_week=data_constants.Day.TUESDAY,
            school=school,
        )

        # Make them into a queryset and use to get a timetable
        lessons = models.Lesson.objects.filter(pk__in=[mon_lesson.pk, tue_lesson.pk])
        tt_object = timetable.Timetable(lessons=lessons, breaks=None)
        tt_dict = tt_object.make_timetable()

        # Check each day has one component, of the same length
        mon = tt_dict[data_constants.Day.MONDAY]
        tue = tt_dict[data_constants.Day.TUESDAY]

        assert len(mon) == len(tue) == 2
        assert mon[0].model_instance == mon_lesson
        assert tue[1].model_instance == tue_lesson

        # Expect 1 free period on either day
        mon_free = mon[1]
        assert mon_free.is_free_period
        assert mon_free.starts_at == dt.time(hour=9)
        assert mon_free.ends_at == dt.time(hour=10)
        assert mon_free.percentage_of_days_timetable == 50

        tue_free = tue[0]
        assert tue_free.is_free_period
        assert tue_free.starts_at == dt.time(hour=8)
        assert tue_free.ends_at == dt.time(hour=9)
        assert tue_free.percentage_of_days_timetable == 50

    def test_make_timetable_from_lesson_and_break_same_day_with_gap(self):
        """Expect the gap to be filled with a free period."""
        school = data_factories.School()

        # Get our two lessons with a gap between them
        lesson = get_lesson_with_slot(
            starts_at=dt.time(hour=8),
            ends_at=dt.time(hour=9),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )
        break_ = data_factories.Break(
            starts_at=dt.time(hour=10),
            ends_at=dt.time(hour=11),
            day_of_week=data_constants.Day.MONDAY,
            school=school,
        )

        # Make them into a queryset and use to get a timetable
        lessons = models.Lesson.objects.filter(pk=lesson.pk)
        breaks = models.Break.objects.filter(pk=break_.pk)
        tt_object = timetable.Timetable(lessons=lessons, breaks=breaks)
        tt_dict = tt_object.make_timetable()

        # Check we have one lesson, one free period, and one break
        mon = tt_dict[data_constants.Day.MONDAY]
        assert len(mon) == 3

        lesson_component = mon[0]
        assert lesson_component.model_instance == lesson
        assert lesson_component.percentage_of_days_timetable == pytest.approx(100 / 3)

        free_period = mon[1]
        assert free_period.starts_at == dt.time(hour=9)
        assert free_period.ends_at == dt.time(hour=10)
        assert free_period.percentage_of_days_timetable == pytest.approx(100 / 3)

        break_component = mon[2]
        assert break_component.model_instance == break_
        assert break_component.percentage_of_days_timetable == pytest.approx(100 / 3)


@pytest.mark.django_db
class TestTimetableMakeTimetableColouring:
    """Tests for the free period colouring in functionality of make_timetable."""

    def test_lessons_with_more_slots_have_lower_colour_rank_than_lesson_with_fewer(
        self,
    ):
        school = data_factories.School()

        slot_0 = data_factories.TimetableSlot(school=school)
        slot_1 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)
        slot_2 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_1)

        # Make some lessons with a varying number of slots
        # Note the ordering is done by *required lessons*, so no need to give them more than 1 slot
        lesson_0 = data_factories.Lesson(
            total_required_slots=10, user_defined_time_slots=(slot_0,), school=school
        )
        lesson_1 = data_factories.Lesson(
            total_required_slots=5, user_defined_time_slots=(slot_1,), school=school
        )
        lesson_2 = data_factories.Lesson(
            total_required_slots=2, user_defined_time_slots=(slot_2,), school=school
        )

        # Make the timetable for these lessons
        lessons = models.Lesson.objects.filter(
            pk__in=[lesson_0.pk, lesson_1.pk, lesson_2.pk]
        )
        tt_object = timetable.Timetable(lessons=lessons, breaks=None)
        tt_dict = tt_object.make_timetable()

        lesson_0_slot = tt_dict[slot_0.day_of_week][0]
        assert lesson_0_slot.model_instance == lesson_0
        assert (
            lesson_0_slot.hexadecimal_color_code
            == view_timetable_constants.Colour.get_colour(rank=0)
        )

        lesson_1_slot = tt_dict[slot_1.day_of_week][1]
        assert lesson_1_slot.model_instance == lesson_1
        assert (
            lesson_1_slot.hexadecimal_color_code
            == view_timetable_constants.Colour.get_colour(rank=1)
        )

        lesson_2_slot = tt_dict[slot_0.day_of_week][2]
        assert lesson_2_slot.model_instance == lesson_2
        assert (
            lesson_2_slot.hexadecimal_color_code
            == view_timetable_constants.Colour.get_colour(rank=2)
        )
