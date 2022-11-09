"""Urls module for the data_upload app"""

# Django imports
from django.urls import path

# Local application imports
from constants.url_names import UrlName
from . import views

urlpatterns = [
    # BASE data upload page
    path('', views.UploadPage.as_view(), name=UrlName.FILE_UPLOAD_PAGE.value),

    # Data UPLOAD endpoints
    path('pupil_upload/', views.PupilListUpload.as_view(), name=UrlName.PUPIL_LIST_UPLOAD.value),
    path('teacher_upload/', views.TeacherListUpload.as_view(), name=UrlName.TEACHER_LIST_UPLOAD.value),
    path('classroom_upload/', views.ClassroomListUpload.as_view(), name=UrlName.CLASSROOM_LIST_UPLOAD.value),
    path('timetable_upload/', views.TimetableStructureUpload.as_view(), name=UrlName.TIMETABLE_STRUCTURE_UPLOAD.value),
    path('unsolved_class_upload/', views.UnsolvedClassUpload.as_view(), name=UrlName.UNSOLVED_CLASSES_UPLOAD.value),
    path('fixed_class_upload/', views.FixedClassUpload.as_view(), name=UrlName.FIXED_CLASSES_UPLOAD.value),

    # Data RESET endpoints
    path('pupil_reset/', views.PupilListReset.as_view(), name=UrlName.PUPIL_LIST_RESET.value),
    path('teacher_reset/', views.TeacherListReset.as_view(), name=UrlName.TEACHER_LIST_RESET.value),
    path('classroom_reset/', views.ClassroomListReset.as_view(), name=UrlName.CLASSROOM_LIST_RESET.value),
    path('timetable_reset/', views.TimetableStructureReset.as_view(), name=UrlName.TIMETABLE_STRUCTURE_RESET.value),
    path('unsolved_class_reset/', views.UnsolvedClassReset.as_view(), name=UrlName.UNSOLVED_CLASSES_RESET.value),
    path('fixed_class_reset/', views.FixedClassReset.as_view(), name=UrlName.FIXED_CLASSES_RESET.value)
]
