"""Module containing integration tests for the LessonFileUploadProcessor"""


# Standard library imports
import datetime as dt

# Third party imports
import pytest

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile

# Local application imports
from data import constants as data_constants
from data import models
from domain.data_management import upload_processors
from domain.data_management.constants import Header
from tests import data_factories
from tests.helpers.csv import get_csv_from_lists


@pytest.mark.django_db
class TestBreakFileUploadProcessorValidUploads:
    """Test that 'break' files can be processed into the db successfully."""

    def test_two_fully_populated_breaks_successful(self):
        # Make some data that the csv file will need to reference
        school = data_factories.School()

        teacher_a = data_factories.Teacher(school=school)
        teacher_b = data_factories.Teacher(school=school)

        yg_a = data_factories.YearGroup(school=school)
        yg_b = data_factories.YearGroup(school=school)

        # Get a csv file-like object
        csv_file = get_csv_from_lists(
            [
                [
                    Header.BREAK_ID,
                    Header.BREAK_NAME,
                    Header.DAY_OF_WEEK,
                    Header.STARTS_AT,
                    Header.ENDS_AT,
                    Header.TEACHER_IDS,
                    Header.RELEVANT_YEAR_GROUP_IDS,
                ],
                [
                    "mon-lunch",
                    "Lunch",
                    data_constants.Day.MONDAY.value,
                    "12:00",
                    "13:00:00",
                    f"{teacher_a.teacher_id}; {teacher_b.teacher_id}",
                    f"{yg_a.year_group_id}; {yg_b.year_group_id}",
                ],
                [
                    "tue-lunch",
                    "Lunch",
                    data_constants.Day.TUESDAY.value,
                    "12:00",
                    "13:00:00",
                    f"{teacher_a.teacher_id}; {teacher_b.teacher_id}",
                    f"{yg_a.year_group_id}; {yg_b.year_group_id}",
                ],
            ]
        )

        # Upload the file
        upload_file = SimpleUploadedFile(name="break.csv", content=csv_file.read())
        upload_processor = upload_processors.BreakFileUploadProcessor(
            csv_file=upload_file, school_access_key=school.school_access_key
        )

        # Check basic outcome of upload
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 2

        # Check saved to db
        breaks = models.Break.objects.filter(school=school)
        assert breaks.count() == 2

        # Check each break instance's fields
        break_a = breaks.get(break_id="mon-lunch")
        assert break_a.day_of_week == data_constants.Day.MONDAY

        break_b = breaks.get(break_id="tue-lunch")
        assert break_b.day_of_week == data_constants.Day.TUESDAY

        for break_ in [break_a, break_b]:
            # All other fields are the same
            assert break_.break_name == "Lunch"
            assert break_.starts_at == dt.time(hour=12)
            assert break_.ends_at == dt.time(hour=13)
            teachers = break_.teachers.all()
            assert (
                teachers.count() == 2
                and teacher_a in teachers
                and teacher_b in teachers
            )
            ygs = break_.relevant_year_groups.all()
            assert ygs.count() == 2 and yg_a in ygs and yg_b in ygs
