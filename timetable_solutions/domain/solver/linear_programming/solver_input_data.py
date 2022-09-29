"""
Module defining the data used by the solver, and how this data is accessed from the data layer
"""

# Local application imports
from data import models


class TimetableSolverInputs:
    def __init__(self, school_id: int):
        """
        Class responsible for loading in all of a school's data and storing it.
        """

        # Store data location
        self.school_id = school_id

        # Call the data layer to get all necessary data
        self.fixed_classes = models.FixedClass.objects.get_all_instances_for_school(school_id=self.school_id)
        self.unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=self.school_id)
        self.timetable_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=self.school_id)
        self.pupils = models.Pupil.objects.get_all_instances_for_school(school_id=self.school_id)
        self.teachers = models.Teacher.objects.get_all_instances_for_school(school_id=self.school_id)
