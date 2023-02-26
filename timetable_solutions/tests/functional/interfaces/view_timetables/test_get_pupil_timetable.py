"""Tests for retrieval & construction of pupil timetables."""

# Standard library imports
import datetime as dt

# Local application imports
from data import models
from data.constants import Day
from interfaces import constants as interfaces_constants
from tests import data_factories
from tests.functional.client import TestClient


class TestPupilTimetable(TestClient):
    @staticmethod
    def get_pupil_with_timetable() -> models.Pupil:
        """Make sufficient data for retrieving a pupil's timetable to be viable"""
        # Constants
        slot_duration = 1
        days = [Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY, Day.FRIDAY]

        # Make the basic school data
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        # Make 6 slots per day, with a free period and break
        slots = []
        for day in days:
            for start_time in [9, 11, 12, 14, 15, 16]:
                slot = data_factories.TimetableSlot(
                    school=school,
                    relevant_year_groups=(yg,),
                    day_of_week=day,
                    starts_at=dt.time(hour=start_time),
                    ends_at=dt.time(hour=start_time + slot_duration),
                )
                slots.append(slot)

        # Make 3 lessons for the pupil
        n_lessons = 3
        for m in range(0, n_lessons):
            data_factories.Lesson(
                school=school,
                pupils=(pupil,),
                user_defined_time_slots=slots[m::n_lessons],
            )

        # Make 1 break per day, 13:00-14:00
        for day in days:
            data_factories.Break(
                school=school,
                relevant_year_groups=(yg,),
                day_of_week=day,
                starts_at=dt.time(hour=13),
                ends_at=dt.time(hour=13 + slot_duration),
            )

        return pupil

    def test_access_pupil_timetable_page_contains_correct_timetable(self):
        # Get a pupil with a timetable, and authorise our client to their school
        pupil = self.get_pupil_with_timetable()
        self.authorise_client_for_school(pupil.school)

        # Navigate to the pupil's timetable
        url = interfaces_constants.UrlName.PUPIL_TIMETABLE.url(pupil_id=pupil.pupil_id)
        response = self.client.get(url)

        assert response.status_code == 200

        # Ensure timetable is as expected
        timetable = response.context["timetable"]
        all_components = [
            component for components in timetable.values() for component in components
        ]

        lessons = [component for component in all_components if component.is_lesson]
        assert len(lessons) == 30

        breaks = [component for component in all_components if component.is_break]
        assert len(breaks) == 5

        free_periods = [
            component for component in all_components if component.is_free_period
        ]
        assert len(free_periods) == 5
