"""
Module containing integration tests for:
- PupilFileUploadProcessor
"""


# Third party imports
import pytest

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile

# Local application imports
from data import models
from domain.data_management import upload_processors
from domain.data_management.constants import Header
from tests import data_factories, utils


@pytest.mark.django_db
class TestPupilFileUploadProcessor:
    def test_valid_pupil_file_creates_pupils_in_db(self):
        # Create a school & year group to associate the pupils with
        school = data_factories.School()
        year_group_a = data_factories.YearGroup(school=school)
        year_group_b = data_factories.YearGroup(school=school)

        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.PUPIL_ID,
                    Header.FIRSTNAME,
                    Header.SURNAME,
                    Header.YEAR_GROUP_ID,
                ],
                [1, "Wether", "Spoon", year_group_a.year_group_id],
                [2, "Wesley", "Hoolahan", year_group_b.year_group_id],
                [3, "David", "Wagner", year_group_a.year_group_id],
            ]
        )

        # Try uploading the file
        upload_file = SimpleUploadedFile(name="pupils.csv", content=csv_file.read())
        upload_processor = upload_processors.PupilFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check the upload was successful
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 3

        # Inspect the db
        pupils = models.Pupil.objects.filter(school=school)
        assert pupils.count() == 3

        wether = pupils.get(pupil_id=1)
        assert wether.firstname == "Wether"
        assert wether.surname == "Spoon"
        assert wether.year_group == year_group_a

        wes = pupils.get(pupil_id=2)
        assert wes.firstname == "Wesley"
        assert wes.surname == "Hoolahan"
        assert wes.year_group == year_group_b

    @pytest.mark.parametrize("missing_data_column", [0, 1, 2, 3])
    def test_file_missing_id_unsuccessful(self, missing_data_column: int):
        # Create a school & year group to associate the pupils with
        school = data_factories.School()
        year_group = data_factories.YearGroup(school=school)

        # Crate a valid second row, then mutate it to be invalid
        second_row = [2, "Wesley", "Hoolahan", year_group.year_group_id]
        second_row[missing_data_column] = None

        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.PUPIL_ID,
                    Header.FIRSTNAME,
                    Header.SURNAME,
                    Header.YEAR_GROUP_ID,
                ],
                [1, "Wether", "Spoon", year_group.year_group_id],
                second_row,
            ]
        )

        # Try uploading the file
        upload_file = SimpleUploadedFile(name="pupils.csv", content=csv_file.read())
        upload_processor = upload_processors.PupilFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check the upload was successful
        assert not upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 0
        assert models.Pupil.objects.filter(school=school).count() == 0
        assert "row 2" in upload_processor.upload_error_message

    def test_file_referencing_non_existent_year_group_fails(self):
        # Create a school to associate the pupils with
        school = data_factories.School()

        csv_file = utils.get_csv_from_lists(
            [
                [
                    Header.PUPIL_ID,
                    Header.FIRSTNAME,
                    Header.SURNAME,
                    Header.YEAR_GROUP_ID,
                ],
                [1, "Wether", "Spoon", 10],  # Year group '10' does not exist
            ]
        )

        # Try uploading the file
        upload_file = SimpleUploadedFile(name="pupils.csv", content=csv_file.read())
        upload_processor = upload_processors.PupilFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check the upload was successful
        assert not upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 0
        assert models.Pupil.objects.filter(school=school).count() == 0
        assert "does not exist" in upload_processor.upload_error_message
