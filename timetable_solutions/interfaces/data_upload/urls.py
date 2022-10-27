"""Urls module for the data_upload app"""

# Django imports
from django.urls import path

# Local application imports
from constants.url_names import UrlName
import interfaces.data_upload.upload_view_base_class
from . import views

urlpatterns = [
    path('', interfaces.data_upload.upload_view_base_class.upload_page_view, name=UrlName.FILE_UPLOAD_PAGE.value),
    path('teacher_list/', views.TeacherListUpload.as_view(), name=UrlName.TEACHER_LIST_UPLOAD.value),
    path('pupil_list/', views.PupilListUpload.as_view(), name=UrlName.PUPIL_LIST_UPLOAD.value),
    path('classroom_list/', views.ClassroomListUpload.as_view(), name=UrlName.CLASSROOM_LIST_UPLOAD.value),
    path('timetable_structure/', views.TimetableStructureUpload.as_view(),
         name=UrlName.TIMETABLE_STRUCTURE_UPLOAD.value),
    path('unsolved_classes/', views.UnsolvedClassUpload.as_view(), name=UrlName.UNSOLVED_CLASSES_UPLOAD.value),
    path('fixed_classes/', views.FixedClassUpload.as_view(), name=UrlName.FIXED_CLASSES_UPLOAD.value),
]
