# Local application imports
from interfaces.constants import UrlName
from tests import data_factories
from tests.functional.client import TestClient


class TestLessonDetailModal(TestClient):
    def test_view_lesson_detail_modal_and_then_close_it(self):
        school = self.create_school_and_authorise_client()

        # Make a lesson to view the detail of in the modal
        lesson = data_factories.Lesson(school=school)

        # And a pupil's timetable to access the lesson from
        # (For the test we do not need to associate the lesson & pupil)
        pupil = data_factories.Pupil(school=school)

        # Our http request must come from a timetable page
        timetable_page_url = UrlName.PUPIL_TIMETABLE.url(pupil_id=pupil.pupil_id)
        timetable_page_absolute_url = f"http://{self.http_host}{timetable_page_url}"

        # Access the lesson modal endpoint
        url = UrlName.LESSON_DETAIL.url(lesson_id=lesson.lesson_id)
        modal = self.hx_get(
            url, extra_headers={"HX-Current-URL": timetable_page_absolute_url}
        )

        # Check response
        assert modal.status_code == 200

        # Ensure modal populated with the correct context
        assert modal.context["modal_is_active"]
        assert modal.context["lesson"] == lesson
        assert modal.context["lesson_title"]

        # Ensure a link to close the modal was given
        close_button = modal.html.find("a", {"id": "close_button"})
        assert close_button.attrs["href"] == timetable_page_url
