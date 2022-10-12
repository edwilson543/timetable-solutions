# Django imports
from django import urls

# Local application imports
from interfaces.create_timetables import views


url_patterns = [
    urls.path("", views.CreateTimetable.as_view(), name="create_timetables")
]
