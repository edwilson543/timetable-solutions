"""
Implementation for inserting the solver solution into the relevant part of the database.
"""

# Local application imports
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
        Method to recover the variable values (1s / 0s) and use these to add slots to the
        'solver_defined_time_slots' on all relevant Lesson instances
        """
        for lesson in self._input_data.lessons:
            solved_timeslot_ids = [var_key.slot_id for var_key, var in self._decision_variables.items() if
                                   (var.varValue == 1.0) and (var_key.lesson_id == lesson.lesson_id)]
            solved_timeslots = self._input_data.timetable_slots.filter(slot_id__in=solved_timeslot_ids)
            if solved_timeslots.count() == 0:
                continue
            else:
                lesson.add_solver_defined_time_slots(time_slots=solved_timeslots)
