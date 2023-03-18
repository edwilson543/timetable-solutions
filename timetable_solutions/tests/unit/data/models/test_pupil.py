"""
Unit tests for methods on the Pupil class
"""

# Third party imports
import pytest

# Django imports
from django.db import IntegrityError

# Local application imports
from data import models
from tests import data_factories


@pytest.mark.django_db
class TestCreateNewPupil:
    def test_create_new_valid_pupil(self):
        # Make a school and year group for the pupil to be associated with
        school = data_factories.School()
        yg = data_factories.YearGroup(school=school)

        # Create a new pupil for the school
        models.Pupil.create_new(
            school_id=school.school_access_key,
            year_group=yg,
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
        pupil = data_factories.Pupil()

        with pytest.raises(IntegrityError):
            models.Pupil.create_new(
                school_id=pupil.school.school_access_key,
                pupil_id=pupil.pupil_id,
                firstname="test",
                surname="test",
                year_group=pupil.year_group,
            )


@pytest.mark.django_db
class TestUpdate:
    @pytest.mark.parametrize("firstname", ["Ed", None])
    @pytest.mark.parametrize("surname", ["Wilson", None])
    def test_updates_name_details_in_db(
        self, firstname: str | None, surname: str | None
    ):
        pupil = data_factories.Pupil()

        pupil.update(firstname=firstname, surname=surname)

        expected_firstname = firstname or pupil.firstname
        expected_surname = surname or pupil.surname

        pupil.refresh_from_db()
        assert pupil.firstname == expected_firstname
        assert pupil.surname == expected_surname

    def test_updates_year_group_in_db(self):
        pupil = data_factories.Pupil()
        yg = data_factories.YearGroup(school=pupil.school)

        pupil.update(year_group=yg)

        pupil.refresh_from_db()
        assert pupil.year_group == yg


@pytest.mark.django_db
class TestDeleteAllInstancesForSchool:
    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all pupils associated with a school
        """
        # Make 2 pupils at the same school
        school_1 = data_factories.School()
        data_factories.Pupil(school=school_1)
        data_factories.Pupil(school=school_1)

        # And a pupil at another school
        school_2 = data_factories.School()
        safe_from_deletion_yg = data_factories.Pupil(school=school_2)

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


@pytest.mark.django_db
class TestQueries:
    def test_get_associated_timeslots(self):
        """
        Test that the correct TimetableSlots are associated with a pupil.
        """
        # Make a year group with a time slot
        yg = data_factories.YearGroup()
        slot_1 = data_factories.TimetableSlot(
            school=yg.school, relevant_year_groups=(yg,)
        )
        data_factories.TimetableSlot()  # A dummy slot that won't be included for the pupil

        # Add the pupil to this year group
        pupil = data_factories.Pupil(school=yg.school, year_group=yg)

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
        pupil = data_factories.Pupil()
        lesson = data_factories.Lesson(school=pupil.school, pupils=(pupil,))

        # Execute test unit
        weekly_lessons = pupil.get_lessons_per_week()

        # Check outcome
        assert weekly_lessons == lesson.total_required_slots

    def test_get_occupied_percentage(self):
        """
        Test that the correct occupied percentage is retrieved for a pupil.
        """
        # Make a pupil and give them a lesson
        pupil = data_factories.Pupil()
        slot = data_factories.TimetableSlot(
            school=pupil.school, relevant_year_groups=(pupil.year_group,)
        )
        data_factories.Lesson(
            school=pupil.school,
            total_required_slots=1,
            pupils=(pupil,),
            user_defined_time_slots=(slot,),
        )

        # Execute test unit
        occupied_percentage = pupil.get_occupied_percentage()

        # Occupied percentage should be 100%, since the pupil has 1 lesson slot and 1 associated slot.
        assert occupied_percentage == 1.0
