"""
Unit tests for methods on the Pupil class
"""


# Third party imports
import pytest

# Django imports
from django.db import IntegrityError

# Local application imports
from data import models
from tests import data_factories as factories


@pytest.mark.django_db
class TestPupil:

    # --------------------
    # Factories tests
    # --------------------

    def test_create_new_valid_pupil(self):
        """
        Tests that we can create and save a Pupil via the create_new method
        """
        # Make a school and year group for the pupil to be associated with
        school = factories.School()
        yg = factories.YearGroup(school=school)

        # Create a new pupil for the school
        models.Pupil.create_new(
            school_id=school.school_access_key,
            year_group_id=yg.year_group_id,
            pupil_id=100,
            firstname="test",
            surname="test",
        )

        # Check outcome
        all_pupils = models.Pupil.objects.all()
        assert all_pupils.count() == 1

        pupil = all_pupils.first()
        assert pupil.school == school
        assert pupil.year_group == yg
        assert pupil.pupil_id == 100
        assert pupil.pk == 1

    def test_create_new_fails_when_pupil_id_not_unique_for_school(self):
        """
        Tests that we can cannot create two Pupils with the same id / school, due to unique_together on the Meta class
        """
        # Make a pupil to prevent uniqueness
        pupil = factories.Pupil()

        # Try to make a pupil with the same school / pupil_id
        with pytest.raises(IntegrityError):
            models.Pupil.create_new(
                school_id=pupil.school.school_access_key,
                pupil_id=pupil.pupil_id,
                firstname="test",
                surname="test",
                year_group_id=pupil.year_group.year_group_id,
            )

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all pupils associated with a school
        """
        # Make 2 pupils at the same school
        school_1 = factories.School()
        factories.Pupil(school=school_1)
        factories.Pupil(school=school_1)

        # And a pupil at another school
        school_2 = factories.School()
        safe_from_deletion_yg = factories.Pupil(school=school_2)

        # Delete all the pupils for school_1
        outcome = models.Pupil.delete_all_instances_for_school(
            school_id=school_1.school_access_key
        )

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.Pupil"] == 2

        all_pupils = models.Pupil.objects.all()
        assert all_pupils.count() == 1
        assert all_pupils.first() == safe_from_deletion_yg

    # --------------------
    # Queries tests
    # --------------------

    def test_check_if_busy_at_time_slot_when_pupil_is_busy_with_lesson(self):
        """
        Pupil should be busy if they're in another lesson at passed slot.
        """
        # Make a pupil and ensure they are busy for some slot
        pupil = factories.Pupil()
        slot = factories.TimetableSlot(
            school=pupil.school, relevant_year_groups=(pupil.year_group,)
        )
        factories.Lesson(
            school=pupil.school, pupils=(pupil,), user_defined_time_slots=(slot,)
        )

        # Execute test unit
        is_busy = pupil.check_if_busy_at_timeslot(slot=slot)

        # Check outcome
        assert is_busy

    def test_check_if_busy_at_time_slot_when_pupil_is_busy_with_break(self):
        """
        Pupil should be busy if they're in a break at passed slot.
        """
        # Make a pupil and ensure they are busy for some slot
        pupil = factories.Pupil()
        slot = factories.TimetableSlot(
            school=pupil.school, relevant_year_groups=(pupil.year_group,)
        )
        factories.Break(
            school=pupil.school,
            relevant_year_groups=(pupil.year_group,),
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            day_of_week=slot.day_of_week,
        )

        # Execute test unit
        is_busy = pupil.check_if_busy_at_timeslot(slot=slot)

        # Check outcome
        assert is_busy

    def test_check_if_busy_at_time_slot_when_pupil_is_not_busy(self):
        """
        Test that the check_if_busy_at_time_slot method returns 'False' when we expect it to
        """
        # Make a pupil and slot, so in the absence of any lessons the pupil is not bust
        pupil = factories.Pupil()
        slot = factories.TimetableSlot(
            school=pupil.school, relevant_year_groups=(pupil.year_group,)
        )

        # Execute test unit
        is_busy = pupil.check_if_busy_at_timeslot(slot=slot)

        # Check outcome
        assert not is_busy

    def test_get_associated_timeslots(self):
        """
        Test that the correct TimetableSlots are associated with a pupil.
        """
        # Make a year group with a time slot
        yg = factories.YearGroup()
        slot_1 = factories.TimetableSlot(school=yg.school, relevant_year_groups=(yg,))
        factories.TimetableSlot()  # A dummy slot that won't be included for the pupil

        # Add the pupil to this year group
        pupil = factories.Pupil(school=yg.school, year_group=yg)

        # Now retrieve the pupil's associated slots
        slots = pupil.get_associated_timeslots()

        # Check only slot 1 was associated with the pupil
        assert slots.count() == 1
        assert slot_1 in slots
        # Therefore the dummy slot wasn't associated

    def test_get_lessons_per_week(self):
        """
        Test that the correct number of lessons per week is retrieved for a pupil.
        """
        # Make a pupil and give them a lesson
        pupil = factories.Pupil()
        lesson = factories.Lesson(school=pupil.school, pupils=(pupil,))

        # Execute test unit
        weekly_lessons = pupil.get_lessons_per_week()

        # Check outcome
        assert weekly_lessons == lesson.total_required_slots

    def test_get_occupied_percentage(self):
        """
        Test that the correct occupied percentage is retrieved for a pupil.
        """
        # Make a pupil and give them a lesson
        pupil = factories.Pupil()
        slot = factories.TimetableSlot(
            school=pupil.school, relevant_year_groups=(pupil.year_group,)
        )
        factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            pupils=(pupil,),
            user_defined_time_slots=(slot,),
        )

        # Execute test unit
        occupied_percentage = pupil.get_occupied_percentage()

        # Occupied percentage should be 100%, since the pupil has 1 lesson slot and 1 associated slot.
        assert occupied_percentage == 1.0
