"""
Unit tests for methods on the YearGroup class and YearGroupQuerySet class.
"""

# Third party imports
import pytest

# Local application imports
from data import models
from tests import factories


@pytest.mark.django_db
class TestYearGroupQuerySet:
    def test_get_all_year_groups_with_pupils_excludes_no_pupil_ygs(self):
        school = factories.School()

        # Create a year group with at least one pupil
        yg_1 = factories.YearGroup(school=school)
        factories.Pupil(year_group=yg_1, school=school)

        # Create a year group with no pupils
        factories.YearGroup(school=school)

        # Execute test unit
        ygs_with_pupils = models.YearGroup.objects.get_all_year_groups_with_pupils(
            school_id=school.school_access_key
        )

        # Check only yg_1 included in queryset
        assert ygs_with_pupils.count() == 1
        assert yg_1 in ygs_with_pupils
        # Therefore we have that the other year group isn't in ygs_with_pupils


@pytest.mark.django_db
class TestYearGroup:

    # --------------------
    # Factories tests
    # --------------------

    @pytest.mark.parametrize("year_group", [10, "10"])
    def test_create_new_valid_year_group_from_string(self, year_group):
        """
        Tests that we can create and save a YearGroup instance via the create_new method
        """
        # Get a school to add the year group to
        school = factories.School()

        # Execute test unit
        yg = models.YearGroup.create_new(
            school_id=school.school_access_key, year_group=year_group
        )

        # Check year group created, and associated with school
        assert yg in models.YearGroup.objects.all()
        assert yg.school == school

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all year groups associated with a school.
        """
        # Get some year groups, for different schools
        school_1 = factories.School()
        factories.YearGroup(school=school_1)
        factories.YearGroup(school=school_1)

        school_2 = factories.School()
        safe_from_deletion_yg = factories.YearGroup(school=school_2)

        # Delete the year groups from the first school
        outcome = models.YearGroup.delete_all_instances_for_school(
            school_id=school_1.school_access_key
        )

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.YearGroup"] == 2

        all_ygs = models.YearGroup.objects.all()
        assert all_ygs.count() == 1
        assert all_ygs.first() == safe_from_deletion_yg

    def test_deleting_all_year_groups_also_deletes_all_pupils(self):
        """
        Test that deleting year groups cascades to pupil deletions.
        """
        # Make some pupils and add them to a year group
        yg = factories.YearGroup()
        factories.Pupil(year_group=yg)
        factories.Pupil(year_group=yg)

        # Delete the year group
        outcome = models.YearGroup.delete_all_instances_for_school(
            school_id=yg.school.school_access_key
        )

        # Check only the first school's year groups were deleted
        deleted_ref = outcome[1]
        assert deleted_ref["data.YearGroup"] == 1
        assert deleted_ref["data.Pupil"] == 2

        assert models.YearGroup.objects.all().count() == 0
        assert models.Pupil.objects.all().count() == 0

    def test_deleting_all_year_groups_doesnt_delete_timetable_slots(self):
        """
        Test that deleting year groups only deletes relationships with TimetableSlots
        """
        # Make a slot relevant to a year group
        yg = factories.YearGroup()
        slot = factories.TimetableSlot(relevant_year_groups=(yg,), school=yg.school)

        # Delete the year group
        outcome = models.YearGroup.delete_all_instances_for_school(
            school_id=yg.school.school_access_key
        )

        # Check what has been deleted
        # The year group should be gone
        deleted_ref = outcome[1]
        assert deleted_ref["data.YearGroup"] == 1
        # The year group - timetable slot refs should be deleted
        assert deleted_ref["data.TimetableSlot_relevant_year_groups"] == 1

        # Check db
        assert models.YearGroup.objects.all().count() == 0

        all_slots = models.TimetableSlot.objects.all()
        assert all_slots.count() == 1
        assert all_slots.first() == slot
