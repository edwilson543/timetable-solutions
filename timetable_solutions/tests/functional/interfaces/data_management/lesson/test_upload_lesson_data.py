"""
Tests for the page allowing users to upload a csv file containing lesson data.
"""

# Third party imports
from webtest import Upload

# Local application imports
from data import models
from domain.data_management.constants import ExampleFile, Header
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient
from tests.helpers.csv import get_csv_from_lists


class TestUploadBreakData(TestClient):
    def test_valid_csv_file_gets_processed_to_db(self):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Make some pupils to reference
        yg = data_factories.YearGroup(school=school)
        pupil_a = data_factories.Pupil(school=school, year_group=yg)
        pupil_b = data_factories.Pupil(school=school, year_group=yg)

        # Make a teacher / classroom for the lesson
        teacher = data_factories.Teacher(school=school)
        classroom = data_factories.Classroom(school=school)

        # Navigate to the upload page
        url = UrlName.LESSON_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Upload some valid break_ data as a csv file
        csv_file = get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    Header.CLASSROOM_ID,
                    Header.TOTAL_SLOTS,
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
                [
                    "maths-a",
                    "Maths",
                    teacher.teacher_id,
                    f"{pupil_a.pupil_id}; {pupil_b.pupil_id}",
                    classroom.classroom_id,
                    3,
                    0,
                    None,  # No user defined slots (default)
                ],
            ]
        )
        upload_file = Upload(filename="lessons.csv", content=csv_file.read())
        form = page.forms["upload-form"]
        form["csv_file"] = upload_file
        response = form.submit()

        # Check response ok
        assert response.status_code == 302
        assert response.location == UrlName.LESSON_LIST.url()

        # Check relevant db content created
        lesson = models.Lesson.objects.get()

        assert lesson.lesson_id == "maths-a"
        assert lesson.teacher == teacher
        assert lesson.classroom == classroom
        pupils = lesson.pupils.all()
        assert pupils.count() == 2 and pupil_a in pupils and pupil_b in pupils
        assert lesson.total_required_slots == 3
        assert lesson.total_required_double_periods == 0
        assert lesson.user_defined_time_slots.all().count() == 0

    def test_invalid_upload_rejected(self):
        self.create_school_and_authorise_client()

        # Navigate to the upload page
        url = UrlName.BREAK_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Create some invalid break_ data (non-unique break_ id)
        form = page.forms["upload-form"]
        csv_file = get_csv_from_lists(
            [
                [
                    Header.LESSON_ID,
                    Header.SUBJECT_NAME,
                    Header.TEACHER_ID,
                    Header.PUPIL_IDS,
                    # missing headers
                    Header.TOTAL_DOUBLES,
                    Header.USER_DEFINED_SLOTS,
                ],
            ]
        )
        upload_file = Upload(filename="lessons.csv", content=csv_file.read())
        form["csv_file"] = upload_file
        response = form.submit()

        # Check response ok and context
        assert response.status_code == 200

        # Check no db content created
        assert not models.Lesson.objects.exists()

    def test_can_download_example_file(self):
        school = data_factories.School()
        self.authorise_client_for_school(school)

        # Navigate to the upload page
        url = UrlName.LESSON_UPLOAD.url()
        page = self.client.get(url)

        # Check response ok
        assert page.status_code == 200

        # Download the example file
        file_response = page.click(href=UrlName.LESSON_DOWNLOAD.url())

        assert file_response.headers["Content-Type"] == "text/csv"
        assert (
            file_response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.LESSON.value}"'
        )
