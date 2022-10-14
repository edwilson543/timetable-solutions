"""
Module defining the data used by the solver, and how this data is accessed from the data layer
"""
# Standard library imports
from dataclasses import dataclass
from functools import cached_property
from typing import List, Tuple

# Local application imports
from data import models


@dataclass(frozen=True)
class SolutionSpecification:
    """
    Data class for storing any parameters relating to how the solution should be generated. These parameters are all
    user-defined.
    :param - whether or not to prevent having one class to be taught more than once in a day, with a gap in between
    either session.
    """
    allow_split_classes_within_each_day: bool
    allow_triple_periods_and_above: bool


class TimetableSolverInputs:
    def __init__(self,
                 school_id: int,
                 solution_specification: SolutionSpecification):
        """
        Class responsible for loading in all of a school's data and storing it.
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

    # Additional attributes derived from the existing attributes
    @property
    def consecutive_slots(self) -> List[Tuple[models.TimetableSlot, models.TimetableSlot]]:
        """
        Method to find which of the timetable slots on the class instance are consecutive.
        Not cached since only accessed once in the application logic (when instantiating double period variables).

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
