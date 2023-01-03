"""
All views relating to the data upload page
"""
from .data_upload_page import UploadPage
from .upload_views import (
    TeacherListUpload,
    ClassroomListUpload,
    PupilListUpload,
    TimetableStructureUpload,
    LessonsUpload,
)
from .reset_views import (
    TeacherListReset,
    ClassroomListReset,
    PupilListReset,
    YearGroupReset,
    TimetableStructureReset,
    LessonReset,
    AllSchoolDataReset,
)
from .download_views import (
    TeacherDownload,
    ClassroomDownload,
    PupilDownload,
    TimetableDownload,
    LessonDownload,
)
