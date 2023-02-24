"""
Integration tests for combinations of processes relating to file upload.
"""


# Standard library imports
from pathlib import Path

# Django imports
from django import http, test, urls
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

# Local application imports
from data import models
from interfaces.constants import UrlName
from interfaces.data_management import forms_legacy as forms


class TestFileUploadIntegration(test.TestCase):

    fixtures = ["user_school_profile.json"]

    def upload_test_file(
        self,
        filename: str,
        url_name: UrlName,
        file_field_name: str,
        base_path: Path,
    ) -> http.HttpResponse:
        """
        :param filename: the name of the csv file we are simulating the upload of
        :param url_name: the url extension for the given test file upload (also dict key in the data post request)
        :param file_field_name: name of the field in the form used to hold the uploaded file
        :param base_path: directory of the file we are uploading
        """
        self.client.login(username="dummy_teacher", password="dt123dt123")
        with open((base_path / filename), "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
        url = urls.reverse(url_name.value)
        response = self.client.post(url, data={file_field_name: upload_file})
        return response

    @staticmethod
    def check_database_status(should_be_populated: bool):
        """
        Method to check whether the database has been populated / reset following the relevant action
        """
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        all_teachers = models.Teacher.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(
            school_id=123456
        )
        all_lessons = models.Lesson.objects.get_all_instances_for_school(
            school_id=123456
        )

        assert all_pupils.count() == 6 * should_be_populated
        assert all_teachers.count() == 11 * should_be_populated
        assert all_classrooms.count() == 12 * should_be_populated
        assert all_slots.count() == 30 * should_be_populated
        assert all_lessons.count() == 12 * should_be_populated

    def test_example_files_given_to_user_actually_upload(self):
        """
        Test to see that if we try and upload the example download files, that it works.
        i.e. the files given to the user as examples are valid.
        """
        # Set test parameters
        base_path = settings.BASE_DIR / settings.MEDIA_ROOT / "example_files"

        # Execute test unit
        self.upload_test_file(
            filename="example_teachers.csv",
            url_name=UrlName.TEACHER_LIST_UPLOAD,
            file_field_name=forms.TeacherListUpload.Meta.file_field_name,
            base_path=base_path,
        )
        self.upload_test_file(
            filename="example_classrooms.csv",
            url_name=UrlName.CLASSROOM_LIST_UPLOAD,
            file_field_name=forms.ClassroomListUpload.Meta.file_field_name,
            base_path=base_path,
        )
        self.upload_test_file(
            filename="example_year_groups.csv",
            url_name=UrlName.YEAR_GROUP_UPLOAD,
            file_field_name=forms.YearGroupUpload.Meta.file_field_name,
            base_path=base_path,
        )
        self.upload_test_file(
            filename="example_pupils.csv",
            url_name=UrlName.PUPIL_LIST_UPLOAD,
            file_field_name=forms.PupilListUpload.Meta.file_field_name,
            base_path=base_path,
        )
        self.upload_test_file(
            filename="example_timetable.csv",
            url_name=UrlName.TIMETABLE_STRUCTURE_UPLOAD,
            file_field_name=forms.TimetableStructureUpload.Meta.file_field_name,
            base_path=base_path,
        )
        self.upload_test_file(
            filename="example_lessons.csv",
            url_name=UrlName.LESSONS_UPLOAD,
            file_field_name=forms.LessonUpload.Meta.file_field_name,
            base_path=base_path,
        )

        # Check outcome
        self.check_database_status(should_be_populated=True)
