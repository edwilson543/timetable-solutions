"""
Module defining the data used by the solver, and how this data is accessed from the data layer
"""
# Standard library imports
from dataclasses import dataclass
import datetime as dt
from functools import cached_property
from typing import List, Tuple, Union, Dict

# Local application imports
from data import models


@dataclass
class SolutionSpecification:
    """
    Data class for storing any parameters relating to how the solution should be generated. These parameters are all
    user-defined. Note tht this dataclass is closely tied to the SolutionSpecification Form subclass

    :param - allow_allow_split_classes_within_each_day whether or not to prevent having one class to be taught more
    than once in a day, with a gap in between either session.
    :param - allow_triple_periods_and_above - self evident, but the way it's implemented is to actually prevent a triple
    period or above, since 3 periods in a row would get counted as 2 doubles.
    :param - optimal_optimal_free_period_time_of_day - the time of day which the user has described as the best time to
    have free periods.
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
    optimal_free_period_time_of_day: Union[str, dt.time] = OptimalFreePeriodOptions.NONE
    ideal_proportion_of_free_periods_at_this_time: float = 1.0


class TimetableSolverInputs:
    def __init__(self,
                 school_id: int,
                 solution_specification: SolutionSpecification):
        """
        Class responsible for loading in all of a school's data and storing it.
        Notes: we group the methods on this class as if it were a django model.
        """

        # Store passed information
        self.school_id = school_id
        self.solution_specification = solution_specification

        # Call the data layer to get all necessary data
        self.fixed_classes = models.FixedClass.objects.get_all_instances_for_school(school_id=self.school_id)
        self.unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=self.school_id)
        self.timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=self.school_id)
        self.pupils = models.Pupil.objects.get_all_instances_for_school(school_id=self.school_id)
        self.teachers = models.Teacher.objects.get_all_instances_for_school(school_id=self.school_id)
        self.classrooms = models.Classroom.objects.get_all_instances_for_school(school_id=self.school_id)

        # Check that solution spec and data are compatible (data that's individually invalid has already been checked)
        self.error_messages = []
        self._check_specification_aligns_with_unsolved_class_data()

    # PROPERTIES
    @property
    def consecutive_slots(self) -> List[Tuple[models.TimetableSlot, models.TimetableSlot]]:
        """
        Method to find which of the timetable slots on the class instance are consecutive.
        Not cached since it's only accessed once.

        :return - as a list, the tuples of consecutive slots. The PURPOSE of these are to understand where are the
        candidates for double periods.
        """
        consecutive_slots = []
        previous_slot = None
        # A key thing to note here is that the Meta class on TimetableSlot pre-orders the slots by week and by day.
        for current_slot in self.timetable_slots:
            if (previous_slot is not None) and (current_slot.day_of_week == previous_slot.day_of_week):
                consecutive_slots.append((previous_slot, current_slot))

            previous_slot = current_slot

        return consecutive_slots

    @cached_property
    def available_days(self) -> List[models.WeekDay]:
        """
        Property method to get the weekdays that the user has specified in their timetable structure. Cached since this
        is called from two of the different constraint on TimetableSolverConstraints.
        :return - days_list - a list of the days, sorted from lowest to highest.
        """
        days = {slot.day_of_week for slot in self.timetable_slots}
        days_list = sorted(list(days))
        return days_list

    @cached_property
    def fixed_class_double_period_counts(self) -> Dict[Tuple[str, models.WeekDay], int]:
        """
        Property counting the user-specified double periods, so that they can be counted where relevant in the
        constraints.
        :return - dict whose keys are the class id (Unsolved or Fixed) and day of the week, and values represent the
        number of double periods that class has on that day.
        """
        doubles = {(fixed_class.class_id, day_of_week):
                   fixed_class.get_double_period_count_on_day(day_of_week=day_of_week) for
                   day_of_week in self.available_days for fixed_class in self.fixed_classes if fixed_class.user_defined}
        non_zero_doubles = {key: value for key, value in doubles.items() if value != 0}
        return non_zero_doubles

    @property
    def timetable_start(self) -> float:
        """
        Property finding the earliest time of day that the timetable starts, as a float on the 24-hour clock
        :return: e.g. if the timetable starts at 9 AM, 9.0 will be returned. Similarly 2:30 PM -> 14.5
        """
        start = min(slot.period_starts_at.hour for slot in self.timetable_slots)
        return start

    @property
    def timetable_finish(self) -> float:
        """
        Property finding the latest time of day that the timetable finishes, as a float on the 24-hour clock
        :return: e.g. if the timetable ends at 5 PM, 17.0 will be returned. Similarly 12:30AM -> 0.5
        Note: the returned time is the time the last periods ends (as opposed to the time the last periods starts
        """
        finish = max(slot.period_starts_at.hour + (slot.period_duration.total_seconds() / 3600) for
                     slot in self.timetable_slots)
        return finish

    # QUERIES
    def get_fixed_class_corresponding_to_unsolved_class(self, unsolved_class_id: str) -> Union[models.FixedClass, None]:
        """
        Method to retrieve the FixedClass instance corresponding to an UnsolvedClass id
        :return either the FixedClass instance, or None if there is not a corresponding instance.

        Note - this could be defined on the FixedClass itself (and is, via the .get_fixed_class...), but is define here
        since it only is used by the solver, and relates to filtering specifically the solver's querysets.
        """
        corresponding_fixed_class = self.fixed_classes.filter(class_id=unsolved_class_id)
        if corresponding_fixed_class.count() == 1:
            return corresponding_fixed_class.first()
        else:
            return None

    def get_time_period_starts_at_from_slot_id(self, slot_id: int) -> dt.time:
        """
        Method to find the time of day that a period starts at.
        :param slot_id: The id of the timetable slot we are searching
        :return: period_starts_at - the time of day when the relevant period starts.
        """
        slot = self.timetable_slots.get(slot_id=slot_id)
        period_starts_at = slot.period_starts_at
        return period_starts_at

    # CHECKS
    def _check_specification_aligns_with_unsolved_class_data(self) -> None:
        """
        Method to check whether it's possible to find a solution which disallows split classes within each day, before
        formulating the lp problem, since we know it would be infeasible.
        Side-effects: Store a user-targeted error message, specifying the options for resolution. Clearly we could just
        resolve directly within this method, but given the different options, the choice is left to the user.
        """
        if not self.solution_specification.allow_split_classes_within_each_day:
            max_required_distinct_days = max(usc.total_slots - usc.n_double_periods for usc in self.unsolved_classes)
            available_distinct_days = len(self.available_days)
            if max_required_distinct_days > available_distinct_days:
                self.error_messages.append("Classes require too many distinct slots to all be on separate days. "
                                           "Please allow this in your solution, or ammend your data!")
