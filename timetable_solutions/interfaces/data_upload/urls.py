"""Urls module for the data_upload app"""

# Django imports
from django.urls import path

# Local application imports
import interfaces.data_upload.upload_view_base_class
from . import views

urlpatterns = [
    path('', interfaces.data_upload.upload_view_base_class.upload_page_view, name='file_upload_page'),
    path('teacher_list/', views.TeacherListUploadView.as_view(), name='teacher_list'),
    path('pupil_list/', views.PupilListUploadView.as_view(), name='pupil_list'),
    path('classroom_list/', views.ClassroomListUploadView.as_view(), name='classroom_list'),
    path('timetable_structure/', views.TimetableStructureUploadView.as_view(), name='timetable_structure'),
    path('unsolved_classes/', views.UnsolvedClassUploadView.as_view(), name='unsolved_classes'),
    path('fixed_classes/', views.FixedClassUploadView.as_view(), name='fixed_classes'),
]
