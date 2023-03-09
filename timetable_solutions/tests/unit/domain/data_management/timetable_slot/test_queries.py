"""
Tests for data management timetable slot queries.
"""

# Third party imports
import pytest

# Local application imports
from domain.data_management.timetable_slot import queries
from tests import data_factories


@pytest.mark.django_db
class TestGetNextIdForSchool:
    def test_gets_next_slot_id_when_school_has_slots(self):
        school = data_factories.School()
        slot_a = data_factories.TimetableSlot(school=school)
        slot_b = data_factories.TimetableSlot(school=school)

        next_id = queries.get_next_slot_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == max(slot_a.slot_id, slot_b.slot_id) + 1

    def test_gets_one_when_school_has_no_slots(self):
        school = data_factories.School()

        next_id = queries.get_next_slot_id_for_school(
            school_id=school.school_access_key
        )

        assert next_id == 1
