"""URLs module for timetable_selector app."""

# Django imports
from django.urls import path

# Local application imports
from . import views

urlpatterns = [
    path('', views.selection_navigator, name='selection_navigator'),
    path('teachers/', views.teacher_navigator, name='teachers_navigator'),
    path('pupils/', views.pupil_navigator, name='pupils_navigator'),
]
