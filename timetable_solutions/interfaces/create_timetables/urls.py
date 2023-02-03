# Django imports
from django import urls

# Local application imports
from interfaces.constants import UrlName
from interfaces.create_timetables import views


urlpatterns = [
    urls.path("", views.CreateTimetable.as_view(), name=UrlName.CREATE_TIMETABLES.value)
]
