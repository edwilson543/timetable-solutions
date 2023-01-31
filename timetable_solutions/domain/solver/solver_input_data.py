"""
Module defining the data used by the solver, and how this data is accessed from the data layer
"""
# Standard library imports
from dataclasses import dataclass
import datetime as dt

# Local application imports
from data import models


@dataclass
class SolutionSpecification:
    """
    Data class for storing any parameters relating to how the solution should be generated. These parameters are all
    user-defined. Note tht this dataclass is closely tied to the SolutionSpecification Form.

    :field allow_split_classes_within_each_day: Whether to prevent having one class to be taught more
    than once in a day, with a gap in between either session.
    :field allow_triple_periods_and_above: Self-evident, but the way it's implemented is to actually prevent a triple
    period or above, since 3 periods in a row would get counted as 2 doubles.
    :field optimal_optimal_free_period_time_of_day: The time of day which the user has described as the best time to
    have free periods.
    :field ideal_proportion_of_free_periods_at_this_time: 1 - the proportion of objective function contributions
    that will be randomly allocated.
    """

    class OptimalFreePeriodOptions:
        """
        Inner class to store the basic options for when the optimal_free_period_time_of_day can be chosen as - beyond
        these, the specific options can only be inferred from the data layer by querying the school's TimetableSlots
        """

        NONE = "NONE"
        MORNING = "MORNING"
        AFTERNOON = "AFTERNOON"

    # Instance attributes
    allow_split_classes_within_each_day: bool
    allow_triple_periods_and_above: bool
    optimal_free_period_time_of_day: str | dt.time = OptimalFreePeriodOptions.NONE
    ideal_proportion_of_free_periods_at_this_time: float = 1.0


class TimetableSolverInputs:
    def __init__(self, school_id: int, solution_specification: SolutionSpecification):
        """
        Class responsible for loading in all of a school's data and storing it.
        Notes: we group the methods on this class as if it were a django model.
        """

        # Store passed information
        self.school_id = school_id
        self.solution_specification = solution_specification

        # Call the data layer to get all necessary data
        self.pupils = models.Pupil.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        self.teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=self.school_id
        )
        self.timetable_slots = (
            models.TimetableSlot.objects.get_all_instances_for_school(
                school_id=self.school_id
            )
        )
        self.classrooms = models.Classroom.objects.get_all_instances_for_school(
            school_id=self.school_id
        )

        # Note this filter is vital, as throughout solving it's assumed
        # that lesson instances have the data (e.g. some pupils) needed.
        self.lessons = models.Lesson.objects.get_lessons_requiring_solving(
            school_id=self.school_id
        )

        # Check that solution spec and data are compatible (data that's individually invalid has already been checked)
        self.error_messages: list[str] = []
        self._check_specification_aligns_with_input_data()

    # --------------------
    # Helper properties / methods for TimetableSolverObjective
    # --------------------

    @property
    def timetable_start_hour_as_float(self) -> float:
        """
        Property finding the earliest time of day that the timetable starts, as a float on the 24-hour clock
        :return: e.g. if the timetable starts at 9 AM, 9.0 will be returned. Similarly, 2:30 PM -> 14.5
        """
        start_hour = min(
            slot.period_starts_at.hour + (slot.period_starts_at.minute / 60)
            for slot in self.timetable_slots
        )
        return start_hour

    @property
    def timetable_finish_hour_as_float(self) -> float:
        """
        Property finding the latest time of day that the timetable finishes, as a float on the 24-hour clock
        :return: e.g. if the timetable ends at 5 PM, 17.0 will be returned.

        Note: 23:30-00:30 is an invalid slot span (see .clean on TimetableSlot), so we don't take modulo 24 at the end.
        """
        finish_hour = max(
            slot.period_ends_at.hour + (slot.period_ends_at.minute / 60)
            for slot in self.timetable_slots
        )
        return finish_hour

    def get_time_period_starts_at_from_slot_id(self, slot_id: int) -> dt.time:
        """
        Method to find the time of day that a period starts at.
        :param slot_id: The id of the timetable slot we are searching
        :return: period_starts_at - the time of day when the relevant period starts.
        """
        slot = self.timetable_slots.get(slot_id=slot_id)
        period_starts_at = slot.period_starts_at
        return period_starts_at

    # --------------------
    # Helper methods for TimetableSolverVariables
    # --------------------

    @staticmethod
    def get_consecutive_slots_for_year_group(
        year_group: models.YearGroup,
    ) -> list[tuple[models.TimetableSlot, models.TimetableSlot]]:
        """
        Find the timetable slots that could form double periods, for the given year group.
        Note that a double period is a Lesson-specific concept, and Lessons only contain one year group.

        :param year_group: The string identifier of the year_group instance
        :return - as a list, the tuples of consecutive slots.
        """
        slots = year_group.slots.all().order_by("day_of_week", "period_starts_at")

        consecutive_slots: list[tuple[models.TimetableSlot, models.TimetableSlot]] = []
        previous_slot = None
        for current_slot in slots:
            if (
                previous_slot is not None
            ) and current_slot.check_if_slots_are_consecutive(other_slot=previous_slot):
                consecutive_slots.append((previous_slot, current_slot))
            previous_slot = current_slot

        return consecutive_slots

    # --------------------
    # Validation methods
    # --------------------

    def _check_specification_aligns_with_input_data(self) -> None:
        """
        Method to check whether it's possible to find a solution which disallows split classes within each day, before
        formulating the lp problem, since we know it would be infeasible.
        Side effects: Store a user-targeted error message, specifying the options for resolution. Clearly we could just
        resolve directly within this method, but given the different options, the choice is left to the user.
        """
        if not self.solution_specification.allow_split_classes_within_each_day:
            for lesson in self.lessons:
                required_distinct_days = (
                    lesson.total_required_slots - lesson.total_required_double_periods
                )
                n_available_distinct_days = len(lesson.get_usable_days_of_week())
                if required_distinct_days > n_available_distinct_days:
                    self.error_messages.append(
                        f"Lesson: {lesson} requires too many distinct slots for the solution timetables to all be "
                        f"on separate days.\n"
                        "Please allow this in your solution, or amend your data!"
                    )

                if lesson.pupils.all().count() == 0:
                    self.error_messages.append(
                        f"Lesson: {lesson} has no pupils, and therefore cannot be solved.\n"
                        f"Please add some!"
                    )

        # Check no existing solution
        for lesson in self.lessons:
            if lesson.solver_defined_time_slots.count() > 0:
                self.error_messages.append(
                    f"{lesson} with solver defined time slot(s) was passed as "
                    f"solver input data!"
                )
