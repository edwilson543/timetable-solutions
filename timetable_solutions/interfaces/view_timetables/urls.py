"""URLs module for view_timetables app."""

# Django imports
from django.urls import path

# Local application imports
from . import views

urlpatterns = [
    path('selection_dash/', views.selection_dashboard, name="selection_dashboard"),
    path('teachers/', views.teacher_navigator, name='teachers_navigator'),
    path('teachers/<int:id>', views.teacher_timetable_view, name='teacher_timetable_view'),
    path('pupils/', views.pupil_navigator, name='pupils_navigator'),
    path('pupils/<int:id>', views.pupil_timetable_view, name='pupil_timetable_view')
]
