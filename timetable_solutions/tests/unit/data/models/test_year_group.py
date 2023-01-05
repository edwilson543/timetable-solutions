"""
Unit tests for methods on the YearGroup class and YearGroupQuerySet class.
"""

# Django imports
from django import test

# Local application imports
from data import models


class TestYearGroup(test.TestCase):

    fixtures = ["user_school_profile.json", "year_groups.json"]

    # FACTORY METHOD TESTS
    def test_create_new_valid_year_group_from_string(self):
        """
        Tests that we can create and save a YearGroup instance via the create_new method
        """
        # Execute test unit
        yg = models.YearGroup.create_new(school_id=123456, year_group="10")

        # Check outcome
        all_yg = models.YearGroup.objects.get_all_instances_for_school(school_id=123456)
        assert yg in all_yg

    def test_create_new_valid_year_group_from_integer(self):
        """
        Tests that we can create and save a YearGroup instance via the create_new method
        """
        # Execute test unit
        yg = models.YearGroup.create_new(school_id=123456, year_group=10)

        # Check outcome
        all_yg = models.YearGroup.objects.get_all_instances_for_school(school_id=123456)
        assert yg in all_yg

    def test_delete_all_instances_for_school_successful(self):
        """
        Test that we can successfully delete all year groups associated with a school
        """
        # Execute test unit
        outcome = models.YearGroup.delete_all_instances_for_school(school_id=123456)

        # Check outcome
        deleted_ref = outcome[1]
        assert deleted_ref["data.YearGroup"] == 3

        all_ygs = models.YearGroup.objects.get_all_instances_for_school(
            school_id=123456
        )
        assert all_ygs.count() == 0

    # TODO -> add tests for unsuccessful deletions once foreign keys to yg model added


class TestYearGroupQuerySet(test.TestCase):

    fixtures = ["user_school_profile.json", "year_groups.json", "pupils.json"]

    def test_get_all_year_groups_with_pupils_excludes_no_pupil_ygs(self):
        """
        The fixture contains 'Reception' with no associated pupils, which we expect to be excluded.
        """
        # Execute test unit
        ygs_with_pupils = models.YearGroup.objects.get_all_year_groups_with_pupils(
            school_id=123456
        )

        # Check outcome
        expected_year_groups = ["1", "2"]
        actual_year_groups = list(ygs_with_pupils.values_list("year_group", flat=True))
        assert expected_year_groups == actual_year_groups
