"""Views for the year group data management functionality."""

# Local application imports
from data import models
from interfaces.constants import UrlName
from interfaces.data_management import serializers
from interfaces.data_management.views import base_views


class YearGroupLanding(base_views.LandingView):
    """Page users arrive at from 'data/yeargroup' on the navbar."""

    model_class = models.YearGroup

    # TODO -> update the urls once implemented
    upload_url = UrlName.TEACHER_UPLOAD
    create_url = UrlName.TEACHER_CREATE
    list_url = UrlName.YEAR_GROUP_LIST

    def has_existing_data(self) -> bool:
        return self.request.user.profile.school.has_year_group_data


class YearGroupList(base_views.ListView):
    """Page displaying all a school's year group data."""

    template_name = "data_management/year-group/year-group-list.html"
    ordering = ["year_group_id"]

    model_class = models.YearGroup
    serializer_class = serializers.YearGroup

    displayed_fields = {
        "year_group_id": "Year group ID",
        "year_group_name": "Year group name",
        "number_pupils": "Number pupils",
    }

    update_url = ""  # TODO -> add once available
