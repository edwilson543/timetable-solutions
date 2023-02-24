"""
Tests for the example file download view classes (via their url endpoints)
"""


# Django imports
from django import test, urls

# Local application imports
from domain.data_management.constants import ExampleFile
from interfaces.constants import UrlName


class TestExampleFileDownloads(test.TestCase):
    """
    Tests that we can successfully download the example files as expected
    """

    # Tests for SUCCESSFUL DOWNLOADS VIA GET REQUESTS
    def test_download_teacher_file_successful(self):
        """
        Tests for downloading the example teachers file
        """
        # Set test parameters
        url = urls.reverse(UrlName.TEACHER_DOWNLOAD.value)

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.headers["Content-Type"] == "text/csv"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.TEACHERS.value}"'
        )

    def test_download_pupil_file_successful(self):
        """
        Tests for downloading the example pupils file
        """
        # Set test parameters
        url = urls.reverse(UrlName.PUPIL_DOWNLOAD.value)

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.headers["Content-Type"] == "text/csv"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.PUPILS.value}"'
        )

    def test_download_year_group_file_successful(self):
        """
        Tests for downloading the example year groups file
        """
        # Set test parameters
        url = urls.reverse(UrlName.YEAR_GROUP_DOWNLOAD.value)

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.headers["Content-Type"] == "text/csv"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.YEAR_GROUPS.value}"'
        )

    def test_download_classroom_file_successful(self):
        """
        Tests for downloading the example classrooms file
        """
        # Set test parameters
        url = urls.reverse(UrlName.CLASSROOM_DOWNLOAD.value)

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.headers["Content-Type"] == "text/csv"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.CLASSROOMS.value}"'
        )

    def test_download_timetable_file_successful(self):
        """
        Tests for downloading the example timetable file
        """
        # Set test parameters
        url = urls.reverse(UrlName.TIMETABLE_DOWNLOAD.value)

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.headers["Content-Type"] == "text/csv"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.TIMETABLE.value}"'
        )

    def test_download_lesson_file_successful(self):
        """
        Tests for downloading the example unsolved class file
        """
        # Set test parameters
        url = urls.reverse(UrlName.LESSONS_DOWNLOAD.value)

        # Execute test unit
        response = self.client.get(url)

        # Check outcome
        assert response.headers["Content-Type"] == "text/csv"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.LESSON.value}"'
        )

    def test_download_pupil_file_successful_via_post_request(self):
        """
        Tests for downloading the example pupils file
        """
        # Set test parameters
        url = urls.reverse(UrlName.PUPIL_DOWNLOAD.value)

        # Execute test unit
        response = self.client.post(url)

        # Check outcome
        assert response.headers["Content-Type"] == "text/csv"
        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="{ExampleFile.PUPILS.value}"'
        )
