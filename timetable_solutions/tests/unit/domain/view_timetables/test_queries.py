# Third party imports
import pytest

# Local application imports
from domain.view_timetables import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetLetterIndexedTeachers:
    def test_teachers_are_indexed_by_surname(self):
        # Make some teachers
        school = data_factories.School()
        teacher_a = data_factories.Teacher(surname="Aswad", school=school)
        teacher_q = data_factories.Teacher(surname="Quito", school=school)

        # Execute test unit
        teachers = queries.get_letter_indexed_teachers(
            school_id=school.school_access_key
        )

        # Check outcome as expected
        assert set(teachers.keys()) == {"A", "Q"}

        a = teachers["A"]
        assert a.count() == 1
        assert a.first() == teacher_a

        q = teachers["Q"]
        assert q.count() == 1
        assert q.first() == teacher_q
