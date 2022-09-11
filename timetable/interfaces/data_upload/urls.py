"""Urls module for the data_upload app"""

# Django imports
from django.urls import path

# Local application imports
import interfaces.data_upload.generic_view_class
from . import views

urlpatterns = [
    path('file_upload/', interfaces.data_upload.generic_view_class.upload_page_view, name='file_upload_page'),
    path('file_upload/teacher_list/', views.TeacherListUploadView.as_view(), name='teacher_list'),
    path('file_upload/pupil_list/', views.PupilListUploadView.as_view(), name='pupil_list'),
    path('file_upload/classroom_list/', views.ClassroomListUploadView.as_view(), name='classroom_list'),
    path('file_upload/timetable_structure/', views.TimetableStructureUploadView.as_view(), name='timetable_structure'),
    path('file_upload/unsolved_classes/', views.UnsolvedClassUploadView.as_view(), name='unsolved_classes'),
    path('file_upload/fixed_classes/', views.FixedClassUploadView.as_view(), name='fixed_classes'),
]
