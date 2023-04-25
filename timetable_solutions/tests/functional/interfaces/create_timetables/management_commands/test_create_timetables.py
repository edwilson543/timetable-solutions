# Third party imports
import pytest

# Django imports
from django.core.management import base as base_command
from django.core.management import call_command

# Local application imports
from tests import data_factories


@pytest.mark.django_db
class TestCreateTimetablesCommand:
    def test_creates_solution(self):
        school = data_factories.School()

        # Create the minimum required data to have something to solve
        yg = data_factories.YearGroup(school=school)
        slot = data_factories.TimetableSlot(school=school, relevant_year_groups=(yg,))
        pupil = data_factories.Pupil(school=school, year_group=yg)
        data_factories.Break(school=school)
        lesson = data_factories.Lesson(
            school=school,
            total_required_slots=1,
            total_required_double_periods=0,
            pupils=(pupil,),
        )

        call_command(
            "create_timetables", f"--school-access-key={school.school_access_key}"
        )

        # Ensure the timetabling problem has actually been solved
        assert lesson.solver_defined_time_slots.get() == slot

    def test_raises_for_non_integer_school_access_key(self):
        with pytest.raises(base_command.CommandError):
            call_command("create_dummy_data", "--school-access-key=access-key")

    def test_raises_if_no_school_access_key_given(self):
        with pytest.raises(base_command.CommandError):
            call_command("create_dummy_data")
