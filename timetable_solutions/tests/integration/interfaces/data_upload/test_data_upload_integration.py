"""
Integration tests for combinations of processes relating to file upload.
"""

# Django imports
from django import http
from django import test
from django import urls
from django.core.files.uploadedfile import SimpleUploadedFile

# Local application imports
from constants.url_names import UrlName
from interfaces.data_upload import forms
from data import models
from tests.input_settings import TEST_DATA_DIR


class TestFileUploadIntegration(test.TestCase):

    fixtures = ["user_school_profile.json"]

    def upload_test_file(self, filename: str, url_name: UrlName, file_field_name: str) -> http.HttpResponse:
        """
        :param filename: the name of the csv file we are simulating the upload of
        :param url_name: the url extension for the given test file upload (also dict key in the data post request)
        :param file_field_name: name of the field in the form used to hold the uploaded file
        """
        self.client.login(username="dummy_teacher", password="dt123dt123")
        with open((TEST_DATA_DIR / "valid_uploads" / filename), "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())
        url = urls.reverse(url_name)
        response = self.client.post(url, data={file_field_name: upload_file})
        return response

    def upload_all_files(self):
        """
        Method to upload all the valid files to the database
        """
        self.upload_test_file(filename="pupils.csv", url_name=UrlName.PUPIL_LIST_UPLOAD.value,
                              file_field_name=forms.PupilListUpload.Meta.file_field_name)
        self.upload_test_file(filename="teachers.csv", url_name=UrlName.TEACHER_LIST_UPLOAD.value,
                              file_field_name=forms.TeacherListUpload.Meta.file_field_name)
        self.upload_test_file(filename="classrooms.csv", url_name=UrlName.CLASSROOM_LIST_UPLOAD.value,
                              file_field_name=forms.ClassroomListUpload.Meta.file_field_name)
        self.upload_test_file(filename="timetable.csv", url_name=UrlName.TIMETABLE_STRUCTURE_UPLOAD.value,
                              file_field_name=forms.TimetableStructureUpload.Meta.file_field_name)
        self.upload_test_file(filename="class_requirements.csv", url_name=UrlName.UNSOLVED_CLASSES_UPLOAD.value,
                              file_field_name=forms.UnsolvedClassUpload.Meta.file_field_name)
        self.upload_test_file(filename="fixed_classes.csv", url_name=UrlName.FIXED_CLASSES_UPLOAD.value,
                              file_field_name=forms.FixedClassUpload.Meta.file_field_name)

    def reset_all_files(self):
        """
        Method to reset all the files for the given user
        """

    @staticmethod
    def check_database_status(should_be_populated: bool):
        """
        Method to check whether the database has been populated / reset following the relevant action
        """
        all_pupils = models.Pupil.objects.get_all_instances_for_school(school_id=123456)
        all_teachers = models.Teacher.objects.get_all_instances_for_school(school_id=123456)
        all_classrooms = models.Classroom.objects.get_all_instances_for_school(school_id=123456)
        all_slots = models.TimetableSlot.objects.get_all_instances_for_school(school_id=123456)
        all_unsolved_classes = models.UnsolvedClass.objects.get_all_instances_for_school(school_id=123456)
        all_fixed_classes = models.FixedClass.objects.get_all_instances_for_school(school_id=123456)

        assert all_pupils.count() == 6 * should_be_populated
        assert all_teachers.count() == 11 * should_be_populated
        assert all_classrooms.count() == 12 * should_be_populated
        assert all_slots.count() == 35 * should_be_populated
        assert all_unsolved_classes.count() == 12 * should_be_populated
        assert all_fixed_classes.count() == 12 * should_be_populated

    def test_upload_reset_upload_all_school_data(self):
        """
        Test that all still works as expected if the user uploads all their data, resets it, and then uploads it again.
        """
        # Initial setup and check
        self.client.login(username="dummy_teacher", password="dt123dt123")
        self.check_database_status(should_be_populated=False)

        for _ in range(0, 2):
            # Upload the files and check it has worked
            self.upload_all_files()
            self.check_database_status(should_be_populated=True)

            # Reset all the files and check it has worked
            url = urls.reverse(UrlName.ALL_DATA_RESET.value)
            self.client.post(url)
            self.check_database_status(should_be_populated=False)
