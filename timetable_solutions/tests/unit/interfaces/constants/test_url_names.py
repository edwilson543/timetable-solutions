# Third party imports
import pytest

# Local application imports
from interfaces.constants import UrlName
from tests import data_factories


class TestUrlName:
    """Tests that the reverse wrappr 'url' method is working as expected."""

    @pytest.mark.parametrize(
        "member,expected_url",
        [
            (UrlName.CREATE_TIMETABLES, "/create/"),
            (UrlName.DASHBOARD, "/users/dashboard/"),
            (UrlName.FILE_UPLOAD_PAGE, "/data/"),
        ],
    )
    def test_reverse_method_without_kwargs(self, member: UrlName, expected_url: str):
        url = member.url()

        assert url == expected_url

    @pytest.mark.django_db
    def test_reverse_method_with_kwargs(self):
        data_factories.Pupil(pk=1)

        url = UrlName.PUPIL_TIMETABLE.url(pupil_id=1)

        assert url == "/view/pupils/1"
