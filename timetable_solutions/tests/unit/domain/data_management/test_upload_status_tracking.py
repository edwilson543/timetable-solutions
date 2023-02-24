"""
Unit test for the upload status tracking mechanism in the domain layer
"""


# Django imports
from django import test

# Local application imports
from data import models
from domain.data_management.upload_status_tracking import (
    UploadStatus,
    UploadStatusTracker,
)


class TestUploadStatusTracker(test.TestCase):
    """
    Unit test for instantiating the UploadStatusTracker dataclass in different ways.
    """

    fixtures = [
        "user_school_profile.json",
        "year_groups.json",
        "classrooms.json",
        "pupils.json",
        "teachers.json",
    ]

    # TODO -> USE FACTORIES
    def test_get_upload_status_matches_the_loaded_fixtures(self):
        """
        Unit test for he get_upload_status method, which instantiates an UploadStatusTracker by querying the database.
        We expect the fixtures loaded by the test class to be 'complete', except for:
        - timetable - not specified as a fixture, so 'incomplete
        - lesson - insufficient uploads - to be 'disallowed'.
        """
        # Set test parameters
        school = models.School.objects.get_individual_school(school_id=123456)

        # Execute test unit
        upload_status = UploadStatusTracker.get_upload_status(school=school)

        # Check outcome
        assert upload_status.year_groups.status == UploadStatus.COMPLETE
        assert upload_status.pupils.status == UploadStatus.COMPLETE
        assert upload_status.teachers.status == UploadStatus.COMPLETE
        assert upload_status.classrooms.status == UploadStatus.COMPLETE
        assert upload_status.timetable.status == UploadStatus.INCOMPLETE
        assert upload_status.lessons.status == UploadStatus.DISALLOWED


class TestUploadStatusTracking:
    # Tests for UploadStatusTracker instantiation
    def test_instantiation_with_all_uploads_as_true_all_converted_to_complete(self):
        """
        Unit test that instantiating an UploadStatusTracker with all init parameters as True converts all upload
        statuses to 'complete'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            year_groups=True,
            pupils=True,
            teachers=True,
            classrooms=True,
            timetable=True,
            lessons=True,
            breaks=True,
        )

        # Check outcome
        assert full_status.year_groups.status == UploadStatus.COMPLETE
        assert full_status.pupils.status == UploadStatus.COMPLETE
        assert full_status.teachers.status == UploadStatus.COMPLETE
        assert full_status.classrooms.status == UploadStatus.COMPLETE
        assert full_status.timetable.status == UploadStatus.COMPLETE
        assert full_status.lessons.status == UploadStatus.COMPLETE
        assert full_status.lessons.status == UploadStatus.COMPLETE

    def test_instantiation_with_all_uploads_as_false_gives_incomplete_and_disallowed(
        self,
    ):
        """
        Unit test that instantiating an UploadStatusTracker with all init parameters as False converts the independent
        tables to 'incomplete', and therefore the tables that depend on these to 'disallowed'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            year_groups=False,
            pupils=False,
            teachers=False,
            classrooms=False,
            timetable=False,
            lessons=False,
            breaks=False,
        )

        # Check outcome
        assert full_status.year_groups.status == UploadStatus.INCOMPLETE
        assert full_status.teachers.status == UploadStatus.INCOMPLETE
        assert full_status.classrooms.status == UploadStatus.INCOMPLETE

        assert full_status.pupils.status == UploadStatus.DISALLOWED
        assert full_status.timetable.status == UploadStatus.DISALLOWED
        assert full_status.lessons.status == UploadStatus.DISALLOWED
        assert full_status.lessons.status == UploadStatus.DISALLOWED

    def test_instantiation_with_single_upload_as_false_disallows_lessons(
        self,
    ):
        """
        Unit test that instantiating an UploadStatusTracker with one init parameter as False (on a dependent table)
        converts the tables that depend on these to 'disallowed'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            year_groups=True,
            pupils=True,
            teachers=True,
            classrooms=True,
            timetable=False,
            lessons=False,
            breaks=False,
        )

        # Check outcome
        assert full_status.year_groups.status == UploadStatus.COMPLETE
        assert full_status.pupils.status == UploadStatus.COMPLETE
        assert full_status.teachers.status == UploadStatus.COMPLETE
        assert full_status.classrooms.status == UploadStatus.COMPLETE
        assert full_status.breaks.status == UploadStatus.INCOMPLETE

        # This file being incomplete forces the lesson file to be disallowed
        assert full_status.timetable.status == UploadStatus.INCOMPLETE

        assert full_status.lessons.status == UploadStatus.DISALLOWED

    def test_instantiation_with_year_groups_as_false_gives_incomplete_and_disallowe(
        self,
    ):
        """
        Unit test that instantiating an UploadStatusTracker with one init parameter as False (on a dependent table)
        converts the tables that depend on these to 'disallowed'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            year_groups=False,
            teachers=True,
            classrooms=True,
            timetable=False,
            pupils=False,
            lessons=False,
            breaks=False,
        )

        # Check outcome
        assert full_status.teachers.status == UploadStatus.COMPLETE
        assert full_status.classrooms.status == UploadStatus.COMPLETE

        # This file being incomplete forces disallowed
        assert full_status.year_groups.status == UploadStatus.INCOMPLETE

        assert full_status.pupils.status == UploadStatus.DISALLOWED
        assert full_status.timetable.status == UploadStatus.DISALLOWED

        assert full_status.breaks.status == UploadStatus.DISALLOWED
        assert full_status.lessons.status == UploadStatus.DISALLOWED

    def test_instantiation_with_only_lesson_uploads_as_false_gives_complete_and_incomplete(
        self,
    ):
        """
        Unit test that instantiating an UploadStatusTracker with all init parameters as True on the dependent tables
        then allows the Lesson table to be uploaded (i.e. marked as 'incomplete', not 'disallowed')
        converts the tables that depend on these to 'disallowed'.
        """
        # Execute test unit
        full_status = UploadStatusTracker(
            year_groups=True,
            pupils=True,
            teachers=True,
            classrooms=True,
            timetable=True,
            lessons=False,
            breaks=False,
        )

        # Check outcome
        assert full_status.year_groups.status == UploadStatus.COMPLETE
        assert full_status.pupils.status == UploadStatus.COMPLETE
        assert full_status.teachers.status == UploadStatus.COMPLETE
        assert full_status.classrooms.status == UploadStatus.COMPLETE
        assert full_status.timetable.status == UploadStatus.COMPLETE

        assert full_status.breaks.status == UploadStatus.INCOMPLETE
        assert full_status.lessons.status == UploadStatus.INCOMPLETE
