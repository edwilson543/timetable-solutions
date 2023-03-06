"""Views for the year group data management functionality."""

# Local application imports
from data import models
from interfaces.constants import UrlName
from interfaces.data_management.views import base_views


class YearGroupLanding(base_views.LandingView):
    """Page users arrive at from 'data/yeargroup' on the navbar."""

    model_class = models.YearGroup

    # TODO -> update the urls once implemented
    upload_url = UrlName.TEACHER_UPLOAD
    create_url = UrlName.TEACHER_CREATE
    list_url = UrlName.TEACHER_LIST

    def has_existing_data(self) -> bool:
        return self.request.user.profile.school.has_year_group_data
