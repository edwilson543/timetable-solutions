"""Unit tests for the instantiation of solver variables."""

# Third party imports
import pytest

# Local application imports
from data import models
from domain import solver as slvr
from tests import data_factories
from tests import domain_factories


def get_variables_maker(school: models.School) -> slvr.TimetableSolverVariables:
    """Utility method used to return an instance of the class holding the timetable variables."""
    spec = domain_factories.SolutionSpecification()
    input_data = slvr.TimetableSolverInputs(
        school_id=school.school_access_key, solution_specification=spec
    )
    variables_maker = slvr.TimetableSolverVariables(
        inputs=input_data, set_variables=False
    )
    return variables_maker


@pytest.mark.django_db
class TestTimetableSolverVariables:
    @pytest.mark.parametrize("m_lessons", [1, 5])
    @pytest.mark.parametrize("n_slots", [1, 7])
    @pytest.mark.parametrize("dummy_slots", [True, False])
    def test_get_decision_variables_one_per_lesson_and_slot(
        self, m_lessons: int, n_slots: int, dummy_slots: bool
    ):
        """
        :param dummy_slots: If set to True then we add some random slots that we
        do not expect to appear in the inspected variables.
        """
        # Make a school with m lessons and n slots
        school = data_factories.School()
        lessons = [
            data_factories.Lesson.with_n_pupils(school=school)
            for _ in range(0, m_lessons)
        ]

        all_year_groups = [lesson.pupils.first().year_group for lesson in lessons]

        for _ in range(0, n_slots):
            data_factories.TimetableSlot(
                school=school, relevant_year_groups=all_year_groups
            )

        if dummy_slots:
            # Make some slots irrelevant to any year groups (and therefore) lessons
            data_factories.TimetableSlot(school=school)
            data_factories.TimetableSlot(school=school)

        # Execute test unit
        variables_maker = get_variables_maker(school=school)
        variables = variables_maker._get_decision_variables()

        # Ensure we have the right number of decision variables
        assert len(variables) == m_lessons * n_slots

        # Ensure all are vars are well-formed
        for var in variables.values():
            assert var.lowBound == 0
            assert var.upBound == 1
            assert var.cat == "Integer"
            assert var.varValue is None

    def test_strip_decision_variables_removes_any_user_defined_slots(self):
        # Make a school with 1 lesson requiring 5 slots
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        slots = [
            data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))
            for _ in range(0, 5)
        ]

        # Make one slot user defined so that it gets stripped
        data_factories.Lesson(
            school=school,
            total_required_slots=5,
            total_required_double_periods=0,
            pupils=(pupil,),
            user_defined_time_slots=(slots[0],),
        )

        # Execute test unit
        variables_maker = get_variables_maker(school=school)
        variables = variables_maker._get_decision_variables(strip=True)

        # Ensure one variable was stripped
        assert len(variables) == 4
        slot_ids = {key.slot_id for key in variables.keys()}
        assert slot_ids == {slot.slot_id for slot in slots[1:]}

        # Ensure all are vars are well-formed
        for var in variables.values():
            assert var.lowBound == 0
            assert var.upBound == 1
            assert var.cat == "Integer"
            assert var.varValue is None

    @pytest.mark.parametrize("dummy_slots", [True, False])
    def test_get_double_period_variables(self, dummy_slots: bool):
        """
        :param dummy_slots: If set to True then we add some random slots that we
        do not expect to appear in the inspected variables.
        """
        # Make a school with 1 lesson and 3 consecutive slots
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)
        pupil = data_factories.Pupil(school=school, year_group=yg)

        slot_0 = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))
        slot_1 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_0)
        slot_2 = data_factories.TimetableSlot.get_next_consecutive_slot(slot_1)

        lesson = data_factories.Lesson(
            school=school,
            total_required_slots=5,
            total_required_double_periods=2,
            pupils=(pupil,),
        )

        if dummy_slots:
            # Make some consecutive slots irrelevant to any year groups (and therefore) lessons
            dummy_slot_0 = data_factories.TimetableSlot(school=school)
            data_factories.TimetableSlot.get_next_consecutive_slot(dummy_slot_0)

        # Execute test unit
        variables_maker = get_variables_maker(school=school)
        variables = variables_maker._get_double_period_variables()

        # We expect 2 double period variables since the doubles could go at either
        # of the pairs of periods (because there are 3 in a row).
        assert len(variables) == 2

        variable_keys = {key for key in variables.keys()}
        assert variable_keys == {
            slvr.doubles_var_key(
                lesson_id=lesson.lesson_id,
                slot_1_id=slot_0.slot_id,
                slot_2_id=slot_1.slot_id,
            ),
            slvr.doubles_var_key(
                lesson_id=lesson.lesson_id,
                slot_1_id=slot_1.slot_id,
                slot_2_id=slot_2.slot_id,
            ),
        }

        # Ensure all are vars are well-formed
        for var in variables.values():
            assert var.lowBound == 0
            assert var.upBound == 1
            assert var.cat == "Integer"
            assert var.varValue is None
