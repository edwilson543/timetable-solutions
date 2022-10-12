# Django imports
from django import urls

# Local application imports
from interfaces.create_timetables import views


urlpatterns = [
    urls.path("", views.CreateTimetable.as_view(), name="create_timetables")
]
