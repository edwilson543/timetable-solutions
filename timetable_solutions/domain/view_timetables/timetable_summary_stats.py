"""
Module providing summary stats for the view timetable app's dashboard
"""

# Standard library imports
from typing import TypedDict, Literal

# Local application imports
from data import constants
from data import models


class _StatsSummary(TypedDict):
    """
    Summary dict provided when the user has existing timetable solutions.
    """

    has_solutions: Literal[True]

    n_pupils: int
    n_teachers: int
    n_solved_lessons: int
    n_solved_slots: int

    daily_solver_lessons: dict[constants.Day, int]
    daily_user_lessons: dict[constants.Day, int]


class _NoStatsSummary(TypedDict):
    """
    Summary dict provided when the user DOES NOT have existing timetable solutions.
    """

    has_solutions: Literal[False]


class SummaryStats:
    """
    Class used to provide basic summary stats on a school's timetables.
    """

    def __init__(self, school_access_key: int) -> None:
        """
        Retrieve all data relevant to the school from db.
        """
        self._school_access_key = school_access_key

        self._all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=school_access_key
        )
        self._all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=school_access_key
        )
        self._all_pupils = models.Pupil.objects.get_all_instances_for_school(
            school_id=school_access_key
        )
        self._all_teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=school_access_key
        )

    # PROPERTIES
    @property
    def summary_stats(self) -> _StatsSummary | _NoStatsSummary:
        """
        Summary stats dictionary produced by thise class - its purpose.
        """
        if not self._has_solutions:
            return {"has_solutions": False}
        else:
            return {
                "has_solutions": True,
                "n_pupils": self._n_pupils,
                "n_teachers": self._n_teachers,
                "n_solved_lessons": self._n_solved_lessons,
                "n_solved_slots": self._n_solved_slots,
                "daily_solver_lessons": self._daily_solver_lessons,
                "daily_user_lessons": self._daily_user_lessons,
            }

    @property
    def _has_solutions(self) -> bool:
        """
        Whether there is anything to summarise - if solver output count is zero, it hasn't been run yet.
        """
        solver_output_count = sum(
            lesson.solver_defined_time_slots.all().count()
            for lesson in self._all_lessons
        )
        return solver_output_count > 0

    @property
    def _n_solved_lessons(self) -> int:
        """
        Get the number of Lesson instances the solver has finished defining.
        """
        return sum(
            1 if lesson.solver_defined_time_slots.all().count() > 0 else 0
            for lesson in self._all_lessons
        )

    @property
    def _n_solved_slots(self) -> int:
        """
        Get the number of slots the solver has solved.
        """
        return sum(
            lesson.solver_defined_time_slots.all().count()
            for lesson in self._all_lessons
        )

    @property
    def _n_pupils(self) -> int:
        """
        Number of pupils timetables have been created for.
        """
        return self._all_pupils.count()

    @property
    def _n_teachers(self) -> int:
        """
        Number of teachers timetables have been created for.
        """
        return self._all_teachers.count()

    @property
    def _daily_solver_lessons(self) -> dict[constants.Day, int]:
        """
        Get the total number of lesson slots produced by the solver on each day.
        """
        all_days = {
            day.label: sum(
                slot.solver_lessons.all().count() if slot.day_of_week == day else 0
                for slot in self._all_slots
            )
            # mypy doesn't recognise IntegerChoices as an iterable
            for day in constants.Day  # type: ignore
        }
        return {k: v for k, v in all_days.items() if v != 0}

    @property
    def _daily_user_lessons(self) -> dict[constants.Day, int]:
        """
        Get the total number of lesson slots defined by the user on each day.
        Note includes things like break and lunch.
        """
        all_days = {
            day.label: sum(
                slot.user_lessons.all().count() if slot.day_of_week == day else 0
                for slot in self._all_slots
            )
            # mypy doesn't recognise IntegerChoices as an iterable
            for day in constants.Day  # type: ignore
        }
        return {k: v for k, v in all_days.items() if v != 0}
