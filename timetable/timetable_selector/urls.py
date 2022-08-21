"""URLs module for timetable_selector app."""

# Django imports
from django.urls import path
from django.views.generic import TemplateView

# Local application imports
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='selection_navigator.html'), name="selection_navigator"),
    path('teachers/', views.teacher_navigator, name='teachers_navigator'),
    path('teachers/<int:id>', views.teacher_timetable_view, name='teacher_timetable_view'),
    path('pupils/', views.pupil_navigator, name='pupils_navigator'),
    path('pupils/<int:id>', views.pupil_timetable_view, name='pupil_timetable_view')
]
