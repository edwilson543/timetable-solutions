"""URLs module for view_timetables app."""

# Django imports
from django.urls import path

# Local application imports
from constants.url_names import UrlName
from . import views

urlpatterns = [
    path('selection_dash/', views.selection_dashboard, name=UrlName.VIEW_TIMETABLES_DASH.value),

    # Pupil URLs
    path('pupils/', views.pupil_navigator, name=UrlName.PUPILS_NAVIGATOR.value),
    path('pupils/<int:pupil_id>', views.pupil_timetable, name=UrlName.PUPIL_TIMETABLE.value),
    path('pupils/<int:pupil_id>/csv_download/', views.pupil_timetable_download_csv,
         name=UrlName.PUPIL_TT_CSV_DOWNLOAD.value),
    path('pupils/<int:pupil_id>/pdf_download', views.pupil_timetable_download_pdf,
         name=UrlName.PUPIL_TT_PDF_DOWNLOAD.value),

    # Teacher URLs
    path('teachers/', views.teacher_navigator, name=UrlName.TEACHERS_NAVIGATOR.value),
    path('teachers/<int:teacher_id>', views.teacher_timetable, name=UrlName.TEACHER_TIMETABLE.value),
    path('teachers/<int:teacher_id>/csv_download/', views.teacher_timetable_download_csv,
         name=UrlName.TEACHER_TT_CSV_DOWNLOAD.value)
]
