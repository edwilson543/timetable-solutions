"""
Unit test for the upload status tracking mechanism in the domain layer
"""

# Django imports
from django import test

# Local application imports
from data import models
from domain.data_upload_processing.upload_status_tracking import UploadStatusTracker, UploadStatus


class TestUploadStatusTracker(test.TestCase):
    """
    Unit test for instantiating the UploadStatusTracker dataclass in different ways.
    """
    fixtures = ["user_school_profile.json", "classrooms.json", "pupils.json", "teachers.json", "timetable.json",
                "fixed_classes_lunch.json"]

    def test_get_upload_status_matches_the_loaded_fixtures(self):
        """
        Unit test for he get_upload_status method, which instantiates an UploadStatusTracker by querying the database.
        We expect the fixtures loaded by the test class to be 'complete', and unsolved_classes
        (not specified as a fixture) as 'incomplete'
        """
        # Set test parameters
        school = models.School.objects.get_individual_school(school_id=123456)

        # Execute test unit
        upload_status = UploadStatusTracker.get_upload_status(school=school)

        # Check outcome
        assert upload_status.pupils == UploadStatus.COMPLETE.value
        assert upload_status.teachers == UploadStatus.COMPLETE.value
        assert upload_status.classrooms == UploadStatus.COMPLETE.value
        assert upload_status.timetable == UploadStatus.COMPLETE.value
        assert upload_status.unsolved_classes == UploadStatus.INCOMPLETE.value
        assert upload_status.fixed_classes == UploadStatus.COMPLETE.value

    # Tests for UploadStatusTracker instantiation
    def test_instantiation_with_all_uploads_as_true_all_converted_to_complete(self):
        """
        Unit test that instantiating an UploadStatusTracker with all init parameters as True converts all upload
        statuses to 'complete'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            pupils=True, teachers=True, classrooms=True, timetable=True, unsolved_classes=True, fixed_classes=True
        )

        # Check outcome
        assert full_status.pupils == UploadStatus.COMPLETE.value
        assert full_status.teachers == UploadStatus.COMPLETE.value
        assert full_status.classrooms == UploadStatus.COMPLETE.value
        assert full_status.timetable == UploadStatus.COMPLETE.value

        assert full_status.unsolved_classes == UploadStatus.COMPLETE.value
        assert full_status.fixed_classes == UploadStatus.COMPLETE.value

    def test_instantiation_with_all_uploads_as_false_gives_incomplete_and_disallowed(self):
        """
        Unit test that instantiating an UploadStatusTracker with all init parameters as False converts the independent
        tables to 'incomplete', and therefore the tables that depend on these to 'disallowed'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            pupils=False, teachers=False, classrooms=False, timetable=False, unsolved_classes=False, fixed_classes=False
        )

        # Check outcome
        assert full_status.pupils == UploadStatus.INCOMPLETE.value
        assert full_status.teachers == UploadStatus.INCOMPLETE.value
        assert full_status.classrooms == UploadStatus.INCOMPLETE.value
        assert full_status.timetable == UploadStatus.INCOMPLETE.value

        assert full_status.unsolved_classes == UploadStatus.DISALLOWED.value
        assert full_status.fixed_classes == UploadStatus.DISALLOWED.value

    def test_instantiation_with_some_uploads_as_false_gives_incomplete_and_disallowed(self):
        """
        Unit test that instantiating an UploadStatusTracker with one init parameter as False (on a dependent table)
        converts the tables that depend on these to 'disallowed'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            pupils=True, teachers=True, classrooms=True, timetable=False, unsolved_classes=False, fixed_classes=False
        )

        # Check outcome
        assert full_status.pupils == UploadStatus.COMPLETE.value
        assert full_status.teachers == UploadStatus.COMPLETE.value
        assert full_status.classrooms == UploadStatus.COMPLETE.value
        assert full_status.timetable == UploadStatus.INCOMPLETE.value  # This file being incomplete forces disallowed

        assert full_status.unsolved_classes == UploadStatus.DISALLOWED.value
        assert full_status.fixed_classes == UploadStatus.DISALLOWED.value

    def test_instantiation_with_only_class_uploads_as_false_gives_complete_and_incomplete(self):
        """
        Unit test that instantiating an UploadStatusTracker with all init parameters as True on the dependent tables
        then allows the unsolved / fixed class tables to be uploaded (i.e. marked as 'incomplete', not 'disallowed')
        converts the tables that depend on these to 'disallowed'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            pupils=True, teachers=True, classrooms=True, timetable=True, unsolved_classes=False, fixed_classes=False
        )

        # Check outcome
        assert full_status.pupils == UploadStatus.COMPLETE.value
        assert full_status.teachers == UploadStatus.COMPLETE.value
        assert full_status.classrooms == UploadStatus.COMPLETE.value
        assert full_status.timetable == UploadStatus.COMPLETE.value

        assert full_status.unsolved_classes == UploadStatus.INCOMPLETE.value
        assert full_status.fixed_classes == UploadStatus.INCOMPLETE.value
