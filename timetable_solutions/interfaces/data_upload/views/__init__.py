"""
All views relating to the data upload page
"""
from .data_upload_page import UploadPage
from .upload_views import (PupilListUpload, TeacherListUpload, ClassroomListUpload, TimetableStructureUpload,
                           LessonsUpload)
from .reset_views import (PupilListReset, TeacherListReset, ClassroomListReset, TimetableStructureReset,
                          LessonReset, AllSchoolDataReset)
from.download_views import PupilDownload, TeacherDownload, ClassroomDownload, TimetableDownload, LessonDownload
