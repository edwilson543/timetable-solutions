# Local application imports
from data import models
from domain.solver.linear_programming.solver import TimetableSolver


class TimetableSolverOutcome:
    """
    Class responsible for extracting results from a solved TimetableSolver, and inserting the outcome into the database.
    """

    def __init__(self,
                 timetable_solver: TimetableSolver):
        self._timetable_solver = timetable_solver
        self._input_data = timetable_solver.input_data
        self._decision_variables = timetable_solver.variables.decision_variables
        self.error_messages = timetable_solver.error_messages

        if len(self.error_messages) == 0:
            self._extract_results()

    def _extract_results(self) -> None:
        """
        Method to recover the variable values (1s / 0s) and use these to create FixedClass instances, and or update
        existing FixedClass instances already with some known time slots
        """
        for unsolved_class in self._input_data.unsolved_classes:
            solved_timeslot_ids = [var_key.slot_id for var_key, var in self._decision_variables.items() if
                                   (var.varValue == 1.0) and (var_key.class_id == unsolved_class.class_id)]
            solved_timeslots = self._input_data.timetable_slots.filter(slot_id__in=solved_timeslot_ids)
            if solved_timeslots.count() == 0:
                continue

            corresponding_fixed_class = self._input_data.fixed_classes.filter(class_id=unsolved_class.class_id)
            if corresponding_fixed_class.count() == 1:
                fixed_class = corresponding_fixed_class.first()
                self._add_slots_to_existing_fixed_class(fixed_class=fixed_class, timeslots=solved_timeslots)
            else:
                self._create_new_fixed_class_from_time_slots(unsolved_class=unsolved_class, timeslots=solved_timeslots)

    @staticmethod
    def _add_slots_to_existing_fixed_class(
            fixed_class: models.FixedClass, timeslots: models.TimetableSlotQuerySet) -> None:
        """
        Method to update an existing fixed class' time_slots field, with the additional time slots that the solver
        has produced. In this case, the user had defined a FixedClass with some required time slots.
        """
        fixed_class.add_time_slots(time_slots=timeslots)

    @staticmethod
    def _create_new_fixed_class_from_time_slots(
            unsolved_class: models.UnsolvedClass, timeslots: models.TimetableSlotQuerySet) -> None:
        """
        Method to create an entirely new FixedClass instance, using an UnsolvedClass instance and the time slots
        produced by the solver. In this case, the user had not defined any required slots via a FixedClass.
        """
        models.FixedClass.create_new(
            school_id=unsolved_class.school.school_access_key, user_defined=False, class_id=unsolved_class.class_id,
            pupils=unsolved_class.pupils.all(), time_slots=timeslots, classroom_id=unsolved_class.classroom.pk,
            subject_name=unsolved_class.subject_name, teacher_id=unsolved_class.teacher.pk
        )
