"""
Module containing integration tests for:
- TeacherFileUploadProcessor
- ClassroomFileUploadProcessor
- YearGroupFileUploadProcessor
"""

# Standard library imports
import io

# Django imports
from django.core.files.uploadedfile import SimpleUploadedFile

# Third party imports
import pytest

# Local application imports
from base_files.settings.base_settings import BASE_DIR
from data import models
from domain import data_upload_processing
from domain.data_upload_processing.constants import Header
from tests import data_factories
from tests import utils


@pytest.mark.django_db
class TestTeacherFileUploadProcessor:
    def test_valid_teachers_file_creates_teachers_in_db(self):
        # Create a school to upload the file to
        school = data_factories.School()

        csv_file = utils.get_csv_from_lists(
            [
                [Header.TEACHER_ID, Header.FIRSTNAME, Header.SURNAME, Header.TITLE],
                [1, "Nims", "Purja", "Mr"],
                [2, "Theresa", "May", "Mrs"],
                [3, "Greg", "Thebaker", "Mr"],
            ]
        )

        # Try uploading the file
        upload_file = SimpleUploadedFile(name="teachers.csv", content=csv_file.read())
        upload_processor = data_upload_processing.TeacherFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check the upload was successful
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 3

        # Inspect the db
        teachers = models.Teacher.objects.filter(school=school)
        assert teachers.count() == 3

        greg = teachers.get(teacher_id=3)
        assert greg.firstname == "Greg"
        assert greg.surname == "Thebaker"
        assert greg.title == "Mr"

    @pytest.mark.parametrize("invalid_id", [1, "invalid"])
    def test_teacher_invalid_id_rejected(self, invalid_id: int | str):
        """
        :param invalid_id: The value to insert into the second row to cause an error.
        The first param value is a duplicate of the first row, and the second is an invalid type.
        """
        # Create a school to upload the file to
        school = data_factories.School()

        csv_file = utils.get_csv_from_lists(
            [
                [Header.TEACHER_ID, Header.FIRSTNAME, Header.SURNAME, Header.TITLE],
                [1, "Nims", "Purja", "Mr"],
                [invalid_id, "Theresa", "May", "Mrs"],  # Uses same id
            ]
        )

        # Try uploading the file
        upload_file = SimpleUploadedFile(name="teachers.csv", content=csv_file.read())
        upload_processor = data_upload_processing.TeacherFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check the upload was unsuccessful
        assert not upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 0

        # Inspect the db
        teachers = models.Teacher.objects.filter(school=school)
        assert teachers.count() == 0


@pytest.mark.django_db
class TestClassroomUploadProcessor:
    def test_valid_classroom_file_creates_teachers_in_db(self):
        # Create a school to upload the file to
        school = data_factories.School()

        csv_file = utils.get_csv_from_lists(
            [
                [Header.CLASSROOM_ID, Header.BUILDING, Header.ROOM_NUMBER],
                [1, "MB", 10],
                [2, "MB", 11],
                [3, "TB", 33],
            ]
        )

        # Try uploading the file
        upload_file = SimpleUploadedFile(name="classrooms.csv", content=csv_file.read())
        upload_processor = data_upload_processing.ClassroomFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check the upload was successful
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 3

        # Inspect the db
        classrooms = models.Classroom.objects.filter(school=school)
        assert classrooms.count() == 3

        greg = classrooms.get(classroom_id=3)
        assert greg.building == "TB"
        assert greg.room_number == 33

    def test_classroom_file_duplicating_classrooom_rejected(self):
        # Create a school to upload the file to
        school = data_factories.School()

        csv_file = utils.get_csv_from_lists(
            [
                [Header.CLASSROOM_ID, Header.BUILDING, Header.ROOM_NUMBER],
                [1, "MB", 10],
                [2, "MB", 10],  # Same classroom as row above
                [3, "TB", 33],
            ]
        )

        # Try uploading the file
        upload_file = SimpleUploadedFile(name="classrooms.csv", content=csv_file.read())
        upload_processor = data_upload_processing.ClassroomFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check the upload was unsuccessful
        assert not upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 0
        assert "not unique" in upload_processor.upload_error_message

        # Inspect the db
        classrooms = models.Classroom.objects.filter(school=school)
        assert classrooms.count() == 0


@pytest.mark.django_db
class TestYearGroupUploadProcessor:
    def test_valid_year_group_file_creates_year_groups_in_db(self):
        # Create a school to upload the file to
        school = data_factories.School()

        csv_file = utils.get_csv_from_lists(
            [
                [Header.YEAR_GROUP_ID, Header.YEAR_GROUP_NAME],
                [1, "1"],
                [2, "Two"],
                [3, "3"],
                [4, "Reception"],
            ]
        )

        # Try uploading the file
        upload_file = SimpleUploadedFile(
            name="year_groups.csv", content=csv_file.read()
        )
        upload_processor = data_upload_processing.YearGroupFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check the upload was successful
        assert upload_processor.upload_successful
        assert upload_processor.n_model_instances_created == 4

        # Inspect the db
        ygs = models.YearGroup.objects.filter(school=school)
        assert ygs.count() == 4

        assert ygs.get(school=school, year_group_id=1).year_group_name == "1"
        assert ygs.get(school=school, year_group_id=2).year_group_name == "Two"
        assert ygs.get(school=school, year_group_id=3).year_group_name == "3"
        assert ygs.get(school=school, year_group_id=4).year_group_name == "Reception"


@pytest.mark.django_db
class TestFileUploadProcessorInvalidMiscellaneous:
    """
    Tests for attempting to upload files which fall in one of the following categories:
        - Incorrect file type (e.g. .png)
        - Bad csv structure (e.g. certain rows have more columns than in the headers)
        - Simulate a resubmitted form -> should not upload the same data twice
    """

    def test_uploading_a_png_file(self):
        """Test that the upload processor will reject a file that does not have the csv extension."""
        school = data_factories.School()

        # Get some random file from the codebase to upload
        png_filepath = BASE_DIR / "interfaces" / "base_static" / "img" / "favicon.png"
        with open(png_filepath, "rb") as png_file:
            upload_file = SimpleUploadedFile(png_file.name, png_file.read())

        # Execute test unit
        upload_processor = data_upload_processing.YearGroupFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        # Check outcome
        assert not upload_processor.upload_successful
        assert ".png" in upload_processor.upload_error_message

        # Check no pupils were created...
        assert models.Pupil.objects.filter(school=school).count() == 0

    def test_resubmitted_upload_is_rejected(self):
        """Test that submitting a file twice gives an error the second time."""
        # Create a school to upload the file to
        school = data_factories.School()

        def csv_file() -> io.BytesIO:
            return utils.get_csv_from_lists(
                [
                    [Header.CLASSROOM_ID, Header.BUILDING, Header.ROOM_NUMBER],
                    [1, "MB", 10],
                    [2, "MB", 25],
                    [3, "TB", 33],
                ]
            )

        # Upload the file the first time
        upload_file = SimpleUploadedFile(
            name="classrooms.csv", content=csv_file().read()
        )
        first_upload_processor = data_upload_processing.ClassroomFileUploadProcessor(
            csv_file=upload_file,
            school_access_key=school.school_access_key,
        )

        assert first_upload_processor.upload_successful

        # Upload the file again
        second_upload_file = SimpleUploadedFile(
            name="classrooms.csv", content=csv_file().read()
        )
        second_upload_processor = data_upload_processing.ClassroomFileUploadProcessor(
            csv_file=second_upload_file,
            school_access_key=school.school_access_key,
        )

        assert not second_upload_processor.upload_successful
