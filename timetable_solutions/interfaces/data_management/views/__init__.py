"""
All views relating to the data upload page
"""
from .data_upload_page import UploadPage
from .upload_views import (
    BreaksUpload,
    ClassroomListUpload,
    PupilListUpload,
    LessonsUpload,
    TeacherListUpload,
    TimetableStructureUpload,
    YearGroupListUpload,
)
from .reset_views import (
    AllSchoolDataReset,
    BreakReset,
    ClassroomListReset,
    PupilListReset,
    LessonReset,
    TeacherListReset,
    TimetableStructureReset,
    YearGroupReset,
)
from .download_views import (
    BreakDownload,
    ClassroomDownload,
    PupilDownload,
    LessonDownload,
    TeacherDownload,
    TimetableDownload,
    YearGroupDownload,
)

from .teacher import TeacherLanding, TeacherSearch
