# Third party imports
import pytest

# Local application imports
from domain.solver.queries import school as school_queries
from tests import data_factories


@pytest.mark.django_db
class TestCheckSchoolHasSufficientDataToCreateTimetables:
    def test_has_sufficient(self):
        school = data_factories.School()

        # Give the school one entry in every db table
        data_factories.Teacher(school=school)
        data_factories.Pupil(school=school)
        data_factories.Classroom(school=school)
        data_factories.YearGroup(school=school)
        data_factories.TimetableSlot(school=school)
        data_factories.Break(school=school)
        data_factories.Lesson(school=school)

        assert school_queries.check_school_has_sufficient_data_to_create_timetables(
            school
        )

    @pytest.mark.parametrize("missing_pupil_data", [True, False])
    @pytest.mark.parametrize("missing_timetable_slot_data", [True, False])
    @pytest.mark.parametrize("missing_break_data", [True, False])
    @pytest.mark.parametrize("missing_lesson_data", [True, False])
    def test_has_insufficient(
        self,
        missing_pupil_data: bool,
        missing_timetable_slot_data: bool,
        missing_break_data: bool,
        missing_lesson_data: bool,
    ):
        school = data_factories.School()

        # Only give the school data if they aren't missing it
        # Note only the tables with relations to other models are tested
        if not missing_pupil_data:
            data_factories.Pupil(school=school)
        if not missing_timetable_slot_data:
            data_factories.TimetableSlot(school=school)
        if not missing_break_data:
            data_factories.Break(school=school)
        if not missing_lesson_data:
            data_factories.Lesson(school=school)

        if (
            missing_pupil_data
            or missing_timetable_slot_data
            or missing_break_data
            or missing_lesson_data
        ):
            assert not school_queries.check_school_has_sufficient_data_to_create_timetables(
                school
            )
